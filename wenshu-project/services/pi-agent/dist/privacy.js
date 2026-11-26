/** 模型出站脱敏；原始映射只保存在本机私有文件。 */
import { readFileSync } from "node:fs";
let mapping;
export function redact(text) {
    if (process.env.MODEL_EGRESS_ALLOWED === "false")
        throw new Error("model egress is not authorized");
    if (!mapping) {
        const path = process.env.PRIVACY_REDACTION_FILE;
        mapping = path ? JSON.parse(readFileSync(path, "utf8")) : {};
    }
    for (const [source, target] of Object.entries(mapping).sort((a, b) => b[0].length - a[0].length))
        text = text.split(source).join(target);
    return text.replace(/\b[A-Za-z]{1,5}\d{6,12}\b/g, "【学号】")
        .replace(/(?<!\d)\d{17}[\dXx](?!\d)/g, "【身份证号】")
        .replace(/(?<!\d)1[3-9]\d{9}(?!\d)/g, "【手机号】")
        .replace(/[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}/g, "【邮箱】");
}
export function redactValues(value) {
    if (typeof value === "string")
        return redact(value);
    if (Array.isArray(value))
        return value.map(redactValues);
    if (value && typeof value === "object")
        return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, redactValues(v)]));
    return value;
}
//# sourceMappingURL=privacy.js.map