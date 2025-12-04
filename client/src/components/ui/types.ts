import type { HTMLAttributes, ReactNode, ButtonHTMLAttributes } from 'react'

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  className?: string
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

export interface StatCardProps {
  title: string
  value: string | number
  color?: 'primary' | 'green' | 'red' | 'yellow' | 'gray'
  trend?: {
    value: string
    direction: 'up' | 'down'
  }
}

export interface BadgeProps {
  children: ReactNode
  variant?: 'default' | 'primary' | 'success' | 'error' | 'warning'
}

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  children: ReactNode
}

export interface EmptyStateProps {
  message: string
  action?: {
    label: string
    onClick: () => void
  }
}

export interface PageHeaderProps {
  title: string
  description?: string
  action?: ReactNode
}

export interface ErrorMessageProps {
  message: string
}
