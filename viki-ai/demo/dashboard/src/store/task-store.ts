import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

export interface TaskState {
  loading: boolean
  tasks: { [key: string]: any }
  error: any
  setTask: (task: any, id: string) => void
  resetTaskStore: () => void
  setLoading: (loading: boolean) => void
  setError: (error: any) => void
}

export const useTaskStore = create<
  TaskState,
  [
    ['zustand/devtools', never],
    ['zustand/persist', unknown],
    ['zustand/immer', never]
  ]
>(
  devtools(
    persist(
      immer(
        (set, get): TaskState => ({
          loading: false,
          tasks: {},
          error: null,
          setTask: (task: any, id: string) => {
            set((state) => {
              state.tasks[id] = task
              state.loading = false
            })
          },
          resetTaskStore: () => {
            set((state) => {
              state.loading = false
              state.tasks = {}
              state.error = null
            })
          },
          setLoading: (loading) => {
            set((state) => {
              state.loading = loading
            })
          },
          setError: (error) => {
            set((state) => {
              state.error = error
            })
          },
        })
      ),
      {
        name: 'taskStore',
      }
    )
  )
)
