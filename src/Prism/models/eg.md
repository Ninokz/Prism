# models example

这套示例将构建一个**“代码解释器”**的提示词。它包含：

1. **角色 (Persona)**: 定义AI为一个特定编程语言的专家。
2. **任务 (Task)**: 指示AI解释一段代码。
3. **输出规格 (Output Spec)**: 要求AI以JSON格式返回结果。
4. **配方 (Recipe)**: 将以上所有部分组合成最终的提示词。

---

## 1. 模板文件 (`*.jinja`)

这些是纯文本文件，是所有内容的源头。

### `templates/tpl_persona_expert.jinja`

```jinja
You are an expert in {{ language }} with a {{ teaching_tone }} teaching style. Your goal is to explain code concepts clearly to a beginner.
```

### `templates/tpl_task_explain_code.jinja`

```jinja
Your task is to explain the following code snippet. Break down its logic, purpose, and key components.
```

### `templates/tpl_output_json.jinja`

```jinja
Format your response as a single, valid JSON object with the following keys:
- "explanation": (string) A detailed, step-by-step explanation of the code.
- "language_detected": (string) The programming language you identified.
- "confidence_score": (number, between 0.0 and 1.0) Your confidence in the language detection. Default to {{ confidence_score_default }}.
```

---

## 2. 数据契约文件 (`*.dataschema.yaml`)

这些文件定义了模板中变量的类型和默认值。

### `dataschemas/ds_persona_input.dataschema.yaml`

```yaml
# ds_persona_input.dataschema.yaml
meta:
  id: ds_persona_input
  name: "Persona Configuration Schema"
  description: "Defines the configurable parameters for the AI persona."
data:
  $schema: "https://json-schema.org/draft/2020-12/schema"
  title: "PersonaInput"
  type: object
  required: [language, teaching_tone]
  additionalProperties: false
  properties:
    language:
      type: string
      description: "The programming language for the persona."
      default: "Python"
    teaching_tone:
      type: string
      description: "The teaching style of the persona."
      enum: ["gentle", "strict", "humorous"]
      default: "gentle"

```

### `dataschemas/ds_output_format.dataschema.yaml`

```yaml
# ds_output_format.dataschema.yaml
meta:
  id: ds_output_format
  name: "JSON Output Format Schema"
  description: "Defines the structure for the JSON output."
data:
  $schema: "https://json-schema.org/draft/2020-12/schema"
  title: "OutputFormat"
  type: object
  required: [confidence_score_default]
  additionalProperties: false
  properties:
    confidence_score_default:
      type: number
      description: "The default confidence score if not otherwise determined."
      default: 0.95
```

---

### 3. 模块文件 (`*.block.yaml`)

这些文件将模板和数据契约“粘合”在一起，形成可重用的组件。

### `blocks/blk_persona.block.yaml`

```yaml
# blk_persona.block.yaml
meta:
  id: blk_persona
  name: "AI Persona Definitions"
  description: "A collection of different AI personas."
block_type: Persona
# 块级兜底：如果变体没有定义 language, 默认是 JavaScript
defaults:
  language: "JavaScript"
variants:
  - id: expert_teacher
    description: "An expert teacher persona."
    # 变体级兜底：覆盖了块级的 language, 并增加了 teaching_tone
    defaults:
      language: "TypeScript"
      teaching_tone: "strict"
    template_id: tpl_persona_expert  # 引用模板
    contract_id: ds_persona_input    # 引用数据契约
```

### `blocks/blk_task.block.yaml`

```yaml
# blk_task.block.yaml
meta:
  id: blk_task
  name: "Core Task Definitions"
  description: "Defines specific tasks for the AI."
block_type: Task
variants:
  - id: explain_code
    description: "A task to explain a code snippet."
    template_id: tpl_task_explain_code
    # 注意：这个变体没有 contract_id，因为它的模板是纯静态的，这是允许的。
```

### `blocks/blk_output.block.yaml`

```yaml
# blk_output.block.yaml
meta:
  id: blk_output
  name: "Output Specifications"
  description: "Defines different output formats."
block_type: OutputSpecification
variants:
  - id: json_detailed
    description: "A detailed JSON output format."
    template_id: tpl_output_json
    contract_id: ds_output_format # 引用数据契约
```

---

## 4. 配方文件 (`*.recipe.yaml`)

这是最终的组装说明书，将所有模块按顺序拼接起来。

### `recipes/rec_code_explainer.recipe.yaml`

```yaml
# rec_code_explainer.recipe.yaml
meta:
  id: rec_code_explainer
  name: "Code Explainer Prompt Recipe"
  description: "A complete prompt for explaining code and returning JSON."

imports:
  # 单实例导入
  persona:
    block_id: blk_persona
    variant_id: expert_teacher
  
  output_spec:
    block_id: blk_output
    variant_id: json_detailed

  # 多实例导入 (这里只用了一个，但演示了其格式)
  tasks:
    - block_id: blk_task
      variant_id: explain_code

composition:
  sequence:
    - block_ref: "persona"
    - literal: "\n\n---\n\n"
    - block_ref: "tasks[0]" # 使用精确引用
    - literal: "\n\n### REQUIRED OUTPUT FORMAT\n"
    - block_ref: "output_spec"

```

这套文件完整地展示了你的系统设计：

- 所有资源都通过ID进行引用，没有内联。
- `block` 可以选择性地包含 `contract_id`。
- `recipe` 清晰地导入依赖，并在 `composition` 中安排顺序。
- `defaults` 的两层覆盖逻辑也在 `blk_persona` 中得到了体现。
