'use client'
import { useState, useEffect } from 'react'
import { RotateCw } from 'lucide-react'
import type { Card } from '@/lib/api'

export default function Flashcard({ card, index, total }: { card: Card; index: number; total: number }) {
  const [flipped, setFlipped] = useState(false)
  // reset to the front whenever a new card arrives
  useEffect(() => { setFlipped(false) }, [card.id])

  return (
    <div
      className={'flashcard' + (flipped ? ' flipped' : '')}
      onClick={() => setFlipped(f => !f)}
      role="button" tabIndex={0}
      onKeyDown={e => { if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); setFlipped(f => !f) } }}
    >
      <div className="flashcard-inner">
        <div className="face front">
          <div className="kicker">
            <span>{card.topic}</span>
            <span>{index + 1} / {total}</span>
          </div>
          <div className="text">{card.front}</div>
          <div className="flip-hint"><RotateCw size={13} /> tap to reveal</div>
        </div>
        <div className="face back">
          <div className="kicker">
            <span>Answer</span>
            <span>{card.source || card.topic}</span>
          </div>
          <div className="text">{card.back}</div>
          <div className="flip-hint">how well did you recall it?</div>
        </div>
      </div>
    </div>
  )
}
