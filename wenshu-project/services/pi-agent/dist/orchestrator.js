import { ANSWER_PROMPT, INTENT_PROMPT, REWRITER_PROMPT, VERIFIER_PROMPT, runAgent, runAgentJson, } from "./agents.js";
import { retrieveChunks } from "./backend.js";
const MAX_VERIFY_RETRY = 2;
function pickTools(tools, names) {
    return tools.filter((t) => names.includes(t.name));
}
function toCitations(chunks) {
    return chunks.map((c) => ({
        doc_id: c.doc_id ?? "",
        doc_title: c.doc_title ?? c.section_title ?? "",
        dept_id: c.dept_id ?? "",
        chunk_index: c.chunk_index ?? 0,
        section_path: c.section_path ?? [],
        snippet: (c.content ?? "").slice(0, 200),
    }));
}
function formatChunks(chunks) {
    return chunks
        .map((c, i) => `[来源${i + 1}] ${c.content ?? ""}`)
        .join("\n\n");
}
export async function answer(runtime, config, input) {
    const sessionId = input.sessionId ?? crypto.randomUUID();
    const allTools = runtime.tools;
    // 1. Intent
    let intentType = "other";
    let deptIds = [];
    let needsCrossDept = false;
    try {
        const intent = (await runAgentJson(runtime, INTENT_PROMPT, `用户问题：${input.query}`, pickTools(allTools, ["list_departments"])));
        intentType = intent.type ?? "other";
        deptIds = (intent.depts ?? []).filter((d) => d && d !== "dept_all");
        needsCrossDept = Boolean(intent.needs_cross_dept);
    }
    catch (err) {
        console.warn("Intent 失败，使用默认:", err);
    }
    // 2. Rewrite
    let queries = [input.query];
    try {
        const rewriter = (await runAgentJson(runtime, REWRITER_PROMPT, `用户问题：${input.query}\n意图：${intentType}`, pickTools(allTools, ["get_glossary"])));
        if (Array.isArray(rewriter.queries) && rewriter.queries.length > 0) {
            queries = rewriter.queries.filter(Boolean);
        }
    }
    catch (err) {
        console.warn("Rewrite 失败，使用原 query:", err);
    }
    // 3. Retrieve（Python 混合检索，多 query 合并去重）
    const resolvedDepts = input.deptIds && input.deptIds.length > 0 ? input.deptIds : deptIds;
    const seen = new Map();
    for (const q of queries) {
        const chunks = await retrieveChunks(config, q, resolvedDepts.length ? resolvedDepts : null, 5);
        for (const c of chunks) {
            if (c._id && !seen.has(c._id))
                seen.set(c._id, c);
        }
    }
    const chunks = [...seen.values()].slice(0, 8);
    // 4. Answer（pi Agent + 工具；可补充检索/查校历）
    let answerText = await runAgent(runtime, ANSWER_PROMPT.replace("{chunks}", formatChunks(chunks) || "（无参考条款）"), input.query, pickTools(allTools, ["lookup_calendar", "retrieve_documents"]));
    // 5. Verify（最多打回 2 次）
    let verification = {
        passed: true,
        score: 1,
        issues: [],
    };
    for (let i = 0; i < MAX_VERIFY_RETRY; i++) {
        try {
            const verdict = (await runAgentJson(runtime, VERIFIER_PROMPT, `用户问题：${input.query}\n参考条款：${formatChunks(chunks)}\n答案：${answerText}`));
            verification = {
                passed: verdict.passed ?? true,
                score: verdict.score ?? 1,
                issues: verdict.issues ?? [],
            };
        }
        catch (err) {
            console.warn("Verify 失败:", err);
            break;
        }
        if (verification.passed)
            break;
        answerText = await runAgent(runtime, ANSWER_PROMPT.replace("{chunks}", formatChunks(chunks)) +
            `\n\n上次回答存在以下问题，请修正：${verification.issues.join("；")}`, input.query, pickTools(allTools, ["lookup_calendar", "retrieve_documents"]));
    }
    return {
        sessionId,
        answer: answerText,
        citations: toCitations(chunks),
        deptIds: resolvedDepts,
        intentType,
        confidence: needsCrossDept ? 0.75 : 0.8,
        verification,
    };
}
//# sourceMappingURL=orchestrator.js.map