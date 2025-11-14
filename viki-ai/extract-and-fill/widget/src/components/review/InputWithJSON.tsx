import { Input, message } from "antd"
import { useCallback, useEffect, useMemo, useState } from "react"

function InputWithJSON(props: any) {

  const objKeys = useMemo(() => {
    try {
      return Object.keys(props.value?.[0])
    } catch (error) {
      return []
    }

  }, [JSON.stringify(props.value?.[0])])

  const {isEdit, setIsEdit, onChange, editCompleteFlag, setEditCompleteFlag} = props;

  let displayValue = ''

  if (props.value?.length) {
    displayValue = props.value.map((v: Record<string, string>) => {
      return objKeys.map((k) => v[k]).join(',')
    }).join('\n')
  }

  const [textAreaValue, setTextAreaValue ] = useState(displayValue)

  useEffect(() => {
    setTextAreaValue(displayValue)
  }, [displayValue])

  const onTextAreaChange = (e: any) => {
    setTextAreaValue(e.target.value)
  }

  const onEditComplete = useCallback(() => {
    try {
      const newValue = textAreaValue.split('\n').map(val => {
        const res: Record<string, any> = {}
        const splittedValues = val.split(',')
        objKeys.map((k, i) => {
          res[k] = splittedValues[i]
        })
        return res
      })
      // setIsEdit(false)
      setEditCompleteFlag(null)
      onChange?.(newValue)
      setTimeout(() => {
        setIsEdit(false)
      })
    } catch (error) {
      // message.error(`There are some errors in setting up ${props.fieldName}'s value`)
    }
  }, [objKeys, onChange, props.fieldName, setEditCompleteFlag, setIsEdit, textAreaValue])

  useEffect(()=>{
    if (editCompleteFlag) {
      onEditComplete()
    }
  }, [editCompleteFlag, onEditComplete])


  if (!isEdit) {
    return <pre>{displayValue}</pre>
  }

  return <Input.TextArea defaultValue={displayValue} value={textAreaValue || displayValue} onChange={onTextAreaChange} />
}

export default InputWithJSON
