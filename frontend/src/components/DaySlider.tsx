export default function DaySlider({
  day,
  onChange,
}: {
  day: number;
  onChange: (day: number) => void;
}) {
  return (
    <div className="card slider-card">
      <div className="slider-row">
        <label htmlFor="day-range">JOUR</label>
        <input
          id="day-range"
          type="range"
          min={0}
          max={10}
          step={1}
          value={day}
          onChange={(e) => onChange(+e.target.value)}
        />
        <span className="current-day">J{day}</span>
        <div className="day-buttons">
          {Array.from({ length: 11 }, (_, d) => (
            <button key={d} className={d === day ? "active" : ""} onClick={() => onChange(d)}>
              {d}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
