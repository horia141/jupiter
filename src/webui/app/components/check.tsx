interface CheckProps {
  isDone: boolean;
  label?: string;
}

export default function CheckComponent({ isDone, label }: CheckProps) {
  return (
    <span style={{ fontSize: "0.75rem" }}>
      {label} {isDone ? "✅" : "✗"}
    </span>
  );
}
