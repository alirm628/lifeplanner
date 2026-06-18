import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { login, me } from '../api/lifeplanner'

export function useSession() {
  return useQuery({
    queryKey: ['session'],
    queryFn: me,
    retry: false,
    enabled: Boolean(localStorage.getItem('lifeplanner_token')),
  })
}

export function useLogin() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) => login(email, password),
    onSuccess: async (data) => {
      localStorage.setItem('lifeplanner_token', data.access_token)
      await queryClient.invalidateQueries({ queryKey: ['session'] })
    },
  })
}

export function logout() {
  localStorage.removeItem('lifeplanner_token')
}

