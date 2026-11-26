export async function backendFetch(config, path, options = {}) {
    const headers = {
        "Content-Type": "application/json",
        ...options.headers,
    };
    if (config.internalApiToken) {
        headers["X-Internal-Token"] = config.internalApiToken;
    }
    const resp = await fetch(`${config.backendUrl}${path}`, {
        ...options,
        headers,
    });
    const body = (await resp.json().catch(() => ({})));
    if (!resp.ok || (body.code ?? 0) !== 0) {
        throw new Error(`backend ${path} 失败(${resp.status}): ${body.message ?? "unknown"}`);
    }
    return body.data;
}
export async function retrieveChunks(config, query, deptIds, topK = 5) {
    const data = await backendFetch(config, "/api/v1/internal/retrieve", {
        method: "POST",
        body: JSON.stringify({ query, dept_ids: deptIds, top_k: topK }),
    });
    return data ?? [];
}
export async function listDepartments(config) {
    return (await backendFetch(config, "/api/v1/internal/departments")) ?? [];
}
export async function getCalendar(config) {
    return backendFetch(config, "/api/v1/internal/calendar");
}
export async function getGlossary(config) {
    return backendFetch(config, "/api/v1/internal/glossary");
}
export async function listPendingFeedback(config) {
    return backendFetch(config, "/api/v1/internal/feedback/pending");
}
export async function submitFeedback(config, payload) {
    await backendFetch(config, "/api/v1/internal/feedback", {
        method: "POST",
        body: JSON.stringify(payload),
    });
}
export async function saveArtifact(config, payload) {
    return backendFetch(config, "/api/v1/internal/artifacts", {
        method: "POST",
        body: JSON.stringify(payload),
    });
}
//# sourceMappingURL=backend.js.map