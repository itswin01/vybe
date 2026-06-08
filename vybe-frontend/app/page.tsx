'use client'
import { useState } from 'react'
import { APIProvider, Map, AdvancedMarker } from '@vis.gl/react-google-maps'

export default function Home() {
  const [groupName, setGroupName] = useState('')
  const [radius, setRadius] = useState(5)
  const [marker, setMarker] = useState<{lat: number, lng: number} | null>(null)
  const [inviteCode, setInviteCode] = useState('')

  const handleMapClick = (e: any) => {
    setMarker({ lat: e.detail.latLng.lat, lng: e.detail.latLng.lng })
  }

  const handleSubmit = async () => {
    if (!groupName || !marker) {
      alert('Enter group name and pick a meeting point')
      return
    }

    const res = await fetch('http://localhost:8000/groups', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: groupName,
        meeting_point_lat: marker.lat,
        meeting_point_lng: marker.lng,
        search_radius_km: radius
      })
    })

    const data = await res.json()
    setInviteCode(data.invite_code)
  }

  return (
    <main className="p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Create a Group</h1>

      <input
        className="w-full border p-2 rounded mb-4"
        placeholder="Group name"
        value={groupName}
        onChange={e => setGroupName(e.target.value)}
      />

      <label className="block mb-2">Search Radius: {radius} km</label>
      <input
        type="range" min={1} max={20} value={radius}
        onChange={e => setRadius(Number(e.target.value))}
        className="w-full mb-4"
      />

      <p className="mb-2 text-sm text-gray-500">Click on the map to set meeting point</p>

      <APIProvider apiKey={process.env.NEXT_PUBLIC_GOOGLE_MAPS_KEY!}>
        <Map
          style={{ width: '100%', height: '400px' }}
          defaultCenter={{ lat: 12.8231, lng: 80.0444 }}
          defaultZoom={14}
          mapId="vybe-map"
          onClick={handleMapClick}
        >
          {marker && <AdvancedMarker position={marker} />}
        </Map>
      </APIProvider>

      {marker && (
        <p className="mt-2 text-sm text-green-600">
          Meeting point: {marker.lat.toFixed(4)}, {marker.lng.toFixed(4)}
        </p>
      )}

      <button
        onClick={handleSubmit}
        className="mt-4 bg-black text-white px-6 py-2 rounded"
      >
        Create Group
      </button>

      {inviteCode && (
        <div className="mt-4 p-4 bg-gray-100 rounded">
          <p className="font-medium">Group created!</p>
          <p className="text-sm mt-1">Share this link:</p>
          <p className="font-mono text-blue-600">localhost:3000/join/{inviteCode}</p>
        </div>
      )}
    </main>
  )
}