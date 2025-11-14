import { useUserProfileContext } from '../contexts/UserProfileContext'

export const useUserProfile = () => {
  return useUserProfileContext()
}