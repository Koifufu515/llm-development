import { buildModels, getMainModel } from "./providers.js";
import { buildTools } from "./tools.js";
export function buildRuntime(config) {
    const models = buildModels(config);
    const model = getMainModel(models, config);
    const tools = buildTools(config);
    return {
        runtime: {
            model,
            streamFn: models.streamSimple.bind(models),
            tools,
        },
        tools,
    };
}
//# sourceMappingURL=runtime.js.map