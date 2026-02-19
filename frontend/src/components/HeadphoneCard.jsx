export default function HeadphoneCard({ headphone, onUpdate, onRemove }) {
  const handleChange = (field, value) => {
    onUpdate(headphone.id, field, value)
  }

  return (
    <div className="card-base space-y-6">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <label className="input-label">Headphone Model Name</label>
          <input
            type="text"
            placeholder="e.g., Sony WH-1000XM4"
            value={headphone.name || ''}
            onChange={(e) => handleChange('name', e.target.value)}
            className="input-base"
          />
        </div>
        <button
          onClick={() => onRemove(headphone.id)}
          className="ml-4 text-red-600 hover:text-red-800 font-medium text-sm mt-8"
        >
          Remove
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="input-label">Price ($)</label>
          <input
            type="number"
            min="0"
            step="0.01"
            placeholder="299.99"
            value={headphone.price}
            onChange={(e) => handleChange('price', parseFloat(e.target.value) || 0)}
            className="input-base"
          />
        </div>

        <div>
          <label className="input-label">Battery Life (hours)</label>
          <input
            type="number"
            min="0"
            step="0.5"
            placeholder="30"
            value={headphone.battery_life}
            onChange={(e) => handleChange('battery_life', parseFloat(e.target.value) || 0)}
            className="input-base"
          />
        </div>

        <div>
          <label className="input-label">Latency (ms)</label>
          <input
            type="number"
            min="0"
            step="1"
            placeholder="30"
            value={headphone.latency}
            onChange={(e) => handleChange('latency', parseFloat(e.target.value) || 0)}
            className="input-base"
          />
        </div>

        <div>
          <label className="input-label">Driver Size (mm)</label>
          <input
            type="number"
            min="0"
            step="0.1"
            placeholder="40"
            value={headphone.driver_size || ''}
            onChange={(e) => handleChange('driver_size', parseFloat(e.target.value) || 0)}
            className="input-base"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="input-label">Device Type</label>
          <select
            value={headphone.device_type}
            onChange={(e) => handleChange('device_type', e.target.value)}
            className="input-base"
          >
            <option value="Wired Earbuds">Wired Earbuds</option>
            <option value="Wireless Earbuds">Wireless Earbuds</option>
            <option value="Over-Ear Wired">Over-Ear Wired</option>
            <option value="Over-Ear Wireless">Over-Ear Wireless</option>
            <option value="Neckband">Neckband</option>
          </select>
        </div>

        <div>
          <label className="input-label">Number of Mics</label>
          <input
            type="number"
            min="0"
            max="16"
            step="1"
            placeholder="4"
            value={headphone.num_mics || ''}
            onChange={(e) => handleChange('num_mics', parseInt(e.target.value) || 0)}
            className="input-base"
          />
        </div>

        <div>
          <label className="input-label">ANC Type</label>
          <select
            value={headphone.anc_type || 'None'}
            onChange={(e) => handleChange('anc_type', e.target.value)}
            className="input-base"
          >
            <option value="None">None</option>
            <option value="Passive">Passive</option>
            <option value="Active">Active</option>
            <option value="Hybrid">Hybrid</option>
            <option value="Adaptive">Adaptive</option>
          </select>
        </div>

        <div>
          <label className="input-label">ANC Effectiveness</label>
          <select
            value={headphone.anc_strength}
            onChange={(e) => handleChange('anc_strength', e.target.value)}
            className="input-base"
          >
            <option value="None">None</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
            <option value="Very High">Very High</option>
          </select>
        </div>

        <div>
          <label className="input-label">Water Resistance</label>
          <select
            value={headphone.water_resistance}
            onChange={(e) => handleChange('water_resistance', e.target.value)}
            className="input-base"
          >
            <option value="None">None</option>
            <option value="IPX4">IPX4</option>
            <option value="IPX5">IPX5</option>
            <option value="IPX7">IPX7</option>
          </select>
        </div>

        <div>
          <label className="input-label">Comfort Score</label>
          <select
            value={headphone.comfort_score}
            onChange={(e) => handleChange('comfort_score', e.target.value)}
            className="input-base"
          >
            <option value="Poor">Poor</option>
            <option value="Average">Average</option>
            <option value="Good">Good</option>
            <option value="Excellent">Excellent</option>
          </select>
        </div>
      </div>

      <div>
        <label className="input-label">Sound Signature</label>
        <select
          value={headphone.sound_signature || 'Balanced'}
          onChange={(e) => handleChange('sound_signature', e.target.value)}
          className="input-base"
        >
          <option value="Bass-heavy">Bass-heavy</option>
          <option value="Neutral">Neutral</option>
          <option value="Bright">Bright</option>
          <option value="V-shaped">V-shaped</option>
          <option value="Balanced">Balanced</option>
        </select>
      </div>
    </div>
  )
}
