//TODO
interface Option {
  description: string,
  value: boolean | string | number
}

interface VariableDescription {
  description : string,
  type: "bool" | "str" | "int" | "option"
  value: boolean | string | number
  options?: Array<Option>
  multiple?: boolean,
}
