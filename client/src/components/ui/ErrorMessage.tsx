interface ErrorMessageProps {
  message?: string
}

export default function ErrorMessage({ message = 'Something went wrong' }: ErrorMessageProps) {
  return (
    <div className="text-center py-12">
      <p className="text-red-500">{message}</p>
    </div>
  )
}
