import { useEffect, useMemo, useRef, useState } from "react"
import { MapPin, X } from "lucide-react"

export const MIN_LOCATION_QUERY_LENGTH = 2

function filterCitySuggestions(cities, query) {
  const normalized = query.trim().toLowerCase()
  if (normalized.length < MIN_LOCATION_QUERY_LENGTH) return []

  return cities
    .filter((city) => city.name.toLowerCase().includes(normalized))
    .slice(0, 8)
}

export default function LocationSearch({
  cities,
  value,
  selectedCityId,
  onChange,
  onSelect,
  onClear,
  label = "Location",
  placeholder = "Search city...",
  className = "",
}) {
  const containerRef = useRef(null)
  const [isOpen, setIsOpen] = useState(false)

  const suggestions = useMemo(
    () => filterCitySuggestions(cities, value),
    [cities, value],
  )

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  const showSuggestions = isOpen && suggestions.length > 0

  return (
    <label ref={containerRef} className={`relative min-w-0 ${className}`}>
      <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        {label}
      </span>
      <div className="relative">
        <MapPin className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <input
          type="text"
          value={value}
          placeholder={placeholder}
          autoComplete="off"
          onChange={(event) => {
            onChange(event.target.value)
            setIsOpen(true)
          }}
          onFocus={() => {
            if (value.trim().length >= MIN_LOCATION_QUERY_LENGTH) {
              setIsOpen(true)
            }
          }}
          className="h-11 w-full rounded-full border border-border bg-card py-2 pl-10 pr-10 text-sm font-semibold text-foreground outline-none transition hover:border-primary/50 focus:border-primary focus:ring-2 focus:ring-primary/20"
        />
        {(value || selectedCityId) && (
          <button
            type="button"
            onClick={() => {
              onClear()
              setIsOpen(false)
            }}
            aria-label="Clear location"
            className="absolute right-3 top-1/2 flex h-6 w-6 -translate-y-1/2 items-center justify-center rounded-full text-muted-foreground transition hover:bg-muted hover:text-foreground"
          >
            <X className="h-3.5 w-3.5" />
          </button>
        )}
      </div>

      {showSuggestions && (
        <ul
          role="listbox"
          className="absolute z-20 mt-2 max-h-56 w-full overflow-y-auto rounded-2xl border border-border bg-card py-2 shadow-[0_12px_40px_rgba(27,36,29,0.12)]"
        >
          {suggestions.map((city) => (
            <li key={city.id}>
              <button
                type="button"
                role="option"
                aria-selected={selectedCityId === city.id}
                onMouseDown={(event) => event.preventDefault()}
                onClick={() => {
                  onSelect(city)
                  setIsOpen(false)
                }}
                className="flex w-full items-center gap-2 px-4 py-2.5 text-left text-sm text-foreground transition hover:bg-primary/5"
              >
                <MapPin className="h-4 w-4 shrink-0 text-primary/70" />
                <span>{city.name}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </label>
  )
}
