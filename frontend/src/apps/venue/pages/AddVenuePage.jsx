import { useEffect, useState } from "react"
import {
  Upload,
  Plus,
  X,
  MapPin,
  Building2,
} from "lucide-react"

export default function AddVenuePage() {
  const [categories, setCategories] = useState([])
  const [locations, setLocations] = useState([])
  const [bookingTypes, setBookingTypes] = useState([])

  const [amenityInput, setAmenityInput] = useState("")
  const [amenities, setAmenities] = useState([])

  const [images, setImages] = useState([])

  const [formData, setFormData] = useState({
    name: "",
    category: "",
    location: "",
    address: "",
    description: "",
    capacity: "",
    bookingType: "",
  })

  useEffect(() => {
    const fetchData = async () => {
      // mock api calls

      setCategories([
        "Auditorium",
        "Sports",
        "Conference",
        "Cafe",
        "Other",
      ])

      setLocations([
        "Thrissur",
        "Kochi",
        "Trivandrum",
        "Calicut",
        "Palakkad",
      ])

      setBookingTypes([
        "Hourly",
        "Session",
        "Full Day",
      ])
    }

    fetchData()
  }, [])

  const addAmenity = () => {
    if (!amenityInput.trim()) return

    setAmenities((prev) => [
      ...prev,
      amenityInput.trim(),
    ])

    setAmenityInput("")
  }

  const removeAmenity = (index) => {
    setAmenities((prev) =>
      prev.filter((_, i) => i !== index)
    )
  }

  const handleImages = (e) => {
    setImages(Array.from(e.target.files))
  }

  const handleSubmit = () => {
    const payload = {
      ...formData,
      amenities,
      images,
    }

    console.log(payload)
  }

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">
          Add New Venue
        </h1>

        <p className="text-muted-foreground">
          Create and publish a venue instantly.
        </p>
      </div>

      <div className="space-y-8">

        {/* Basic Info */}

        <section className="rounded-xl border bg-white p-6">
          <h2 className="font-semibold text-lg mb-5">
            Basic Information
          </h2>

          <div className="grid md:grid-cols-2 gap-5">

            <div>
              <label>Venue Name *</label>
              <input
                className="input"
                value={formData.name}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    name: e.target.value,
                  })
                }
              />
            </div>

            <div>
              <label>Category *</label>

              <select
                className="input"
                value={formData.category}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    category: e.target.value,
                  })
                }
              >
                <option>Select Category</option>

                {categories.map((item) => (
                  <option key={item}>
                    {item}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label>Booking Type *</label>

              <select
                className="input"
                value={formData.bookingType}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    bookingType: e.target.value,
                  })
                }
              >
                <option>Select Booking Type</option>

                {bookingTypes.map((item) => (
                  <option key={item}>
                    {item}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label>Capacity *</label>

              <input
                type="number"
                className="input"
                value={formData.capacity}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    capacity: e.target.value,
                  })
                }
              />
            </div>
          </div>
        </section>

        {/* Location */}

        <section className="rounded-xl border bg-white p-6">
          <h2 className="font-semibold text-lg mb-5">
            Location Information
          </h2>

          <div className="grid md:grid-cols-2 gap-5">

            <div>
              <label>Location *</label>

              <input
                list="locations"
                className="input"
                placeholder="Search location..."
                value={formData.location}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    location: e.target.value,
                  })
                }
              />

              <datalist id="locations">
                {locations.map((item) => (
                  <option
                    key={item}
                    value={item}
                  />
                ))}
              </datalist>
            </div>

            <div>
              <label>Address *</label>

              <input
                className="input"
                value={formData.address}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    address: e.target.value,
                  })
                }
              />
            </div>
          </div>
        </section>

        {/* Description */}

        <section className="rounded-xl border bg-white p-6">
          <h2 className="font-semibold text-lg mb-5">
            Venue Details
          </h2>

          <textarea
            rows={5}
            className="input"
            placeholder="Describe your venue..."
            value={formData.description}
            onChange={(e) =>
              setFormData({
                ...formData,
                description: e.target.value,
              })
            }
          />
        </section>

        {/* Amenities */}

        <section className="rounded-xl border bg-white p-6">
          <h2 className="font-semibold text-lg mb-5">
            Amenities
          </h2>

          <div className="flex gap-3">
            <input
              className="input flex-1"
              placeholder="Add amenity"
              value={amenityInput}
              onChange={(e) =>
                setAmenityInput(e.target.value)
              }
            />

            <button
              onClick={addAmenity}
              className="btn btn-primary"
            >
              <Plus size={18} />
            </button>
          </div>

          <div className="flex flex-wrap gap-2 mt-4">
            {amenities.map((item, index) => (
              <div
                key={index}
                className="flex items-center gap-2 rounded-full bg-muted px-3 py-2"
              >
                {item}

                <button
                  onClick={() =>
                    removeAmenity(index)
                  }
                >
                  <X size={14} />
                </button>
              </div>
            ))}
          </div>
        </section>

        {/* Images */}

        <section className="rounded-xl border bg-white p-6">
          <h2 className="font-semibold text-lg mb-5">
            Venue Images
          </h2>

          <label className="border-2 border-dashed rounded-xl p-12 flex flex-col items-center cursor-pointer">
            <Upload size={40} />

            <span className="mt-3">
              Upload Venue Images
            </span>

            <input
              type="file"
              multiple
              hidden
              onChange={handleImages}
            />
          </label>

          <p className="mt-3 text-sm text-muted-foreground">
            {images.length} image(s) selected
          </p>
        </section>

        {/* Submit */}

        <div className="flex justify-end gap-3">
          <button className="btn btn-outline">
            Cancel
          </button>

          <button
            onClick={handleSubmit}
            className="btn btn-primary"
          >
            Create Venue
          </button>
        </div>
      </div>
    </div>
  )
}