'use client'
import { masteryColor } from '@/lib/api'

export default function MasteryRing({ value, size = 52 }: { value: number; size?: number }) {
  const stroke = 5
  const r = (size - stroke) / 2
  const circ = 2 * Math.PI * r
  const offset = circ * (1 - Math.max(0, Math.min(100, value)) / 100)
  const color = masteryColor(value)
  return (
    <svg width={size} height={size} style={{ flexShrink: 0 }} aria-label={`Mastery ${value}%`}>
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--line)" strokeWidth={stroke} strokeOpacity={0.6} />
      <circle
        cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeWidth={stroke}
        strokeLinecap="round" strokeDasharray={circ} strokeDashoffset={offset}
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
        style={{ transition: 'stroke-dashoffset .6s cubic-bezier(.2,.8,.2,1)' }}
      />
      <text x="50%" y="50%" dominantBaseline="central" textAnchor="middle"
        fontFamily="'Fraunces', serif" fontWeight={600} fontSize={size * 0.3} fill="var(--bright)">
        {value}
      </text>
    </svg>
  )
}
