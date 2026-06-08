'use client'
import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'

export default function JoinPage() {
  const { invite_code } = useParams()
  const [groupName, setGroupName] = useState('')
  const [name, setName] = useState('')
  const [budget, setBudget] = useState('1')
  const [vibe, setVibe] = useState('cafe')
  const [submitted, setSubmitted] = useState(false)

  useEffect(() => {
    fetch(`http://localhost:8000/groups/invite/${invite_code}`)
      .then(r => r.json())
      .then(d => setGroupName(d.group_name))
  }, [invite_code])

  const handleJoin = async () => {
    if (!name) {
      alert('Enter your name')
      return
    }

    const res = await fetch('http://localhost:8000/members/join', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        invite_code,
        name,
        budget: parseInt(budget),
        vibe
      })
    })

    const data = await res.json()
    if (data.error) {
      alert(data.error)
      return
    }
    setSubmitted(true)
  }

  if (submitted) return <main className="p-8"><h1 className="text-2xl font-bold">Preferences submitted! Waiting for others...</h1></main>

  return (
    <main className="p-8 max-w-md mx-auto">
      <h1 className="text-2xl font-bold mb-2">Join Group</h1>
      {groupName && <p className="text-gray-500 mb-6">Group: {groupName}</p>}

      <input
        className="w-full border p-2 rounded mb-4"
        placeholder="Your name"
        value={name}
        onChange={e => setName(e.target.value)}
      />

      <label className="block mb-2 font-medium">Budget</label>
      <select
        className="w-full border p-2 rounded mb-4"
        value={budget}
        onChange={e => setBudget(e.target.value)}
      >
        <option value="1">Budget (₹)</option>
        <option value="2">Moderate (₹₹)</option>
        <option value="3">Premium (₹₹₹)</option>
      </select>

      <label className="block mb-2 font-medium">Vibe</label>
      <select
        className="w-full border p-2 rounded mb-4"
        value={vibe}
        onChange={e => setVibe(e.target.value)}
      >
        <option value="cafe">Cafe</option>
        <option value="food">Food</option>
        <option value="study">Study</option>
        <option value="hangout">Hangout</option>
      </select>

      <button
        onClick={handleJoin}
        className="w-full bg-black text-white py-2 rounded"
      >
        Submit Preferences
      </button>
    </main>
  )
}