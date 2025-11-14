import { useEffect } from 'react'

const useScript = (url: string, requiredFields: string[]) => {
  useEffect(() => {
    if (requiredFields.every((f) => !!f)) {
      const script = document.createElement('script')

      script.src = url
      script.async = true

      document.body.appendChild(script)
      return () => {
        document.body.removeChild(script)
      }
    }
  }, [url, requiredFields])
}

export default useScript
