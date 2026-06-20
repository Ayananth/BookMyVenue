import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import {
  Upload,
  Plus,
  X,
  MapPin,
  Building2,
  Sparkles,
  FileText,
  Image as ImageIcon,
  Users,
  Clock,
  ArrowLeft,
  CheckCircle,
  HelpCircle,
  Phone
} from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import api from "@/lib/axios"

export default function AddVenuePage() {
  const navigate = useNavigate()

  const [categories, setCategories] = useState([])
  const [locations, setLocations] = useState([])
  const [bookingTypes, setBookingTypes] = useState([])

  const [amenityInput, setAmenityInput] = useState("")
  const [amenities, setAmenities] = useState([])

  const [images, setImages] = useState([])
  const [uploading, setUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false)

  const [formData, setFormData] = useState({
    name: "",
    category: "",
    location: "",
    address: "",
    description: "",
    capacity: "",
    bookingType: "",
    contactName: "",
    contactPhone: "",
    contactEmail: "",

  })

  useEffect(() => {
    const fetchData = async () => {
      // Mock API calls
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

    if (amenities.includes(amenityInput.trim())) {
      setAmenityInput("")
      return
    }

    setAmenities((prev) => [...prev, amenityInput.trim()])
    setAmenityInput("")
  }

  const removeAmenity = (index) => {
    setAmenities((prev) => prev.filter((_, i) => i !== index))
  }

const handleImages = async (e) => {
  if (!e.target.files) return

  await uploadFiles(
    Array.from(e.target.files)
  )
}

  const uploadSingleImage = async (file) => {
    const formData = new FormData();

    formData.append("file", file);

    const response = await api.post(
      "/uploads/image",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

    return response.data;
  };

  const removeImage = (index) => {
    setImages((prev) => prev.filter((_, i) => i !== index))
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

const handleDrop = async (e) => {
  e.preventDefault()
  setIsDragging(false)

  const files = Array.from(
    e.dataTransfer.files
  ).filter((file) =>
    file.type.startsWith("image/")
  )

  await uploadFiles(files)
}

  const handleSubmit = () => {
    const payload = {
      ...formData,
      amenities,
      images,
    }
    console.log("Submitting Venue:", payload)
  }

  // Calculate Form Completion Progress
  const requiredFields = [
    formData.name,
    formData.category,
    formData.bookingType,
    formData.capacity,
    formData.location,
    formData.address,
    formData.description,
  ]
  const completedRequired = requiredFields.filter((val) => val && val.toString().trim() !== "").length
  const totalRequired = requiredFields.length

  const totalSteps = totalRequired + 2 // 7 fields + amenities + images
  const completedSteps =
    completedRequired + (amenities.length > 0 ? 1 : 0) + (images.length > 0 ? 1 : 0)
  const progressPercent = Math.round((completedSteps / totalSteps) * 100)

  // Framer Motion Variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.08,
      },
    },
  }

  const cardVariants = {
    hidden: { opacity: 0, y: 15 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: "spring",
        stiffness: 90,
        damping: 14,
      },
    },
  }



const uploadFiles = async (files) => {
  setUploading(true)

  try {
    const uploadedImages = await Promise.all(
      files.map(async (file, index) => {
        const result = await uploadSingleImage(file)

        return {
          public_id: result.public_id,
          image_url: result.secure_url,
          is_cover: false,
          sort_order: images.length + index + 1,
        }
      })
    )

    setImages((prev) => {
      const merged = [...prev, ...uploadedImages]

      if (merged.length > 0) {
        merged[0].is_cover = true
      }

      return merged
    })

  } finally {
    setUploading(false)
  }
}





















  return (
    <div className="max-w-6xl mx-auto py-2 px-1">
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <button
            onClick={() => navigate(-1)}
            className="group inline-flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground mb-3 transition-colors cursor-pointer"
          >
            <ArrowLeft size={16} className="group-hover:-translate-x-0.5 transition-transform" />
            Back to Venues
          </button>
          <h1 className="font-serif text-3xl md:text-4xl font-bold tracking-tight text-foreground">
            Add New Venue
          </h1>
          <p className="text-muted-foreground mt-1 text-sm md:text-base">
            Create and publish a venue to showcase on our booking website.
          </p>
        </div>

        {/* Progress Tracker Widget */}
        <div className="bg-white/80 border border-border/80 rounded-2xl p-4 shadow-sm backdrop-blur-sm min-w-[240px]">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Form Completion
            </span>
            <span className="text-sm font-bold text-primary">
              {progressPercent}%
            </span>
          </div>
          <div className="w-full bg-secondary h-2.5 rounded-full overflow-hidden">
            <motion.div
              className="bg-primary h-full rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progressPercent}%` }}
              transition={{ duration: 0.4, ease: "easeOut" }}
            />
          </div>
          <span className="text-[11px] text-muted-foreground mt-1 block">
            {completedSteps} of {totalSteps} details completed
          </span>
        </div>
      </div>

      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start"
      >
        {/* Main Form Area */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Info Section */}
          <motion.section
            variants={cardVariants}
            className="rounded-2xl border border-border/60 bg-white/70 backdrop-blur-sm p-6 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="flex items-center gap-3 border-b border-border/40 pb-4 mb-6">
              <div className="p-2 rounded-xl bg-primary/10 text-primary">
                <Building2 size={20} />
              </div>
              <div>
                <h2 className="font-semibold text-lg text-foreground">
                  Basic Information
                </h2>
                <p className="text-xs text-muted-foreground">
                  Identify your venue's core title, category, and target seating.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Venue Name */}
              <div className="md:col-span-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground/90 mb-2 block">
                  Venue Name <span className="text-accent font-bold">*</span>
                </label>
                <input
                  type="text"
                  placeholder="e.g., Grand Palace Ballroom"
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

              {/* Category */}
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground/90 mb-2 block">
                  Category <span className="text-accent font-bold">*</span>
                </label>
                <div className="relative">
                  <select
                    className="input appearance-none bg-[url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%235E6B5F%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E')] bg-[length:0.65rem_auto] bg-[right_1rem_center] bg-no-repeat pr-10"
                    value={formData.category}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        category: e.target.value,
                      })
                    }
                  >
                    <option value="">Select Category</option>
                    {categories.map((item) => (
                      <option key={item} value={item}>
                        {item}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Booking Type */}
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground/90 mb-2 block">
                  Booking Type <span className="text-accent font-bold">*</span>
                </label>
                <div className="relative">
                  <select
                    className="input appearance-none bg-[url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%235E6B5F%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E')] bg-[length:0.65rem_auto] bg-[right_1rem_center] bg-no-repeat pr-10"
                    value={formData.bookingType}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        bookingType: e.target.value,
                      })
                    }
                  >
                    <option value="">Select Booking Type</option>
                    {bookingTypes.map((item) => (
                      <option key={item} value={item}>
                        {item}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Capacity */}
              <div className="md:col-span-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground/90 mb-2 block">
                  Capacity (Max Guests) <span className="text-accent font-bold">*</span>
                </label>
                <input
                  type="number"
                  placeholder="e.g., 250"
                  min="1"
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
          </motion.section>

          {/* Location Section */}
          <motion.section
            variants={cardVariants}
            className="rounded-2xl border border-border/60 bg-white/70 backdrop-blur-sm p-6 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="flex items-center gap-3 border-b border-border/40 pb-4 mb-6">
              <div className="p-2 rounded-xl bg-primary/10 text-primary">
                <MapPin size={20} />
              </div>
              <div>
                <h2 className="font-semibold text-lg text-foreground">
                  Location Information
                </h2>
                <p className="text-xs text-muted-foreground">
                  Help clients navigate to your venue location.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* City/Region */}
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground/90 mb-2 block">
                  City / Location <span className="text-accent font-bold">*</span>
                </label>
                <input
                  list="locations"
                  className="input"
                  placeholder="Search city/location..."
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
                    <option key={item} value={item} />
                  ))}
                </datalist>
              </div>

              {/* Full Address */}
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground/90 mb-2 block">
                  Full Address <span className="text-accent font-bold">*</span>
                </label>
                <input
                  type="text"
                  placeholder="e.g., 5th Avenue, Palace Road"
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
          </motion.section>

{/* Contact Information Section */}
<motion.section
  variants={cardVariants}
  className="rounded-2xl border border-border/60 bg-white/70 backdrop-blur-sm p-6 shadow-sm hover:shadow-md transition-shadow"
>
  <div className="flex items-center gap-3 border-b border-border/40 pb-4 mb-6">
    <div className="p-2 rounded-xl bg-primary/10 text-primary">
      <Phone size={20} />
    </div>

    <div>
      <h2 className="font-semibold text-lg text-foreground">
        Contact Information
      </h2>

      <p className="text-xs text-muted-foreground">
        Booking inquiries and customer communication details.
      </p>
    </div>
  </div>

  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

    {/* Contact Name */}
    <div>
      <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground/90 mb-2 block">
        Contact Person
      </label>

      <input
        type="text"
        className="input"
        placeholder="John Doe"
        value={formData.contactName}
        onChange={(e) =>
          setFormData({
            ...formData,
            contactName: e.target.value,
          })
        }
      />
    </div>

    {/* Contact Phone */}
    <div>
      <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground/90 mb-2 block">
        Contact Phone
      </label>

      <input
        type="tel"
        className="input"
        placeholder="+91 9876543210"
        value={formData.contactPhone}
        onChange={(e) =>
          setFormData({
            ...formData,
            contactPhone: e.target.value,
          })
        }
      />
    </div>

    {/* Contact Email */}
    <div className="md:col-span-2">
      <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground/90 mb-2 block">
        Contact Email
      </label>

      <input
        type="email"
        className="input"
        placeholder="booking@venue.com"
        value={formData.contactEmail}
        onChange={(e) =>
          setFormData({
            ...formData,
            contactEmail: e.target.value,
          })
        }
      />
    </div>
  </div>
</motion.section>

          {/* Description Section */}
          <motion.section
            variants={cardVariants}
            className="rounded-2xl border border-border/60 bg-white/70 backdrop-blur-sm p-6 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="flex items-center gap-3 border-b border-border/40 pb-4 mb-6">
              <div className="p-2 rounded-xl bg-primary/10 text-primary">
                <FileText size={20} />
              </div>
              <div>
                <h2 className="font-semibold text-lg text-foreground">
                  Venue Details
                </h2>
                <p className="text-xs text-muted-foreground">
                  Provide an attractive description detailing key qualities and highlights.
                </p>
              </div>
            </div>

            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground/90 mb-2 block">
                Description <span className="text-accent font-bold">*</span>
              </label>
              <textarea
                rows={5}
                className="input resize-none"
                placeholder="Write something engaging about the venue environment, availability, layout, acoustics, or parking..."
                value={formData.description}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    description: e.target.value,
                  })
                }
              />
            </div>
          </motion.section>
        </div>

        {/* Sidebar Widgets (Column 3) */}
        <div className="space-y-6">
          {/* Real-time Summary Card Preview */}
          <motion.section
            variants={cardVariants}
            className="rounded-2xl border border-border/60 bg-white/80 backdrop-blur-sm p-5 shadow-sm overflow-hidden"
          >
            <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground/80 px-2.5 py-1 bg-secondary rounded-full inline-block mb-4">
              Real-Time Preview
            </span>

            <div className="rounded-xl overflow-hidden border border-border/40 bg-card">
              {/* Preview Image */}
              <div className="h-44 bg-secondary relative flex items-center justify-center text-muted-foreground overflow-hidden">
                {images[0]?.image_url ? (
                  <img
                    src={images[0]?.image_url}
                    alt="Venue Preview"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="flex flex-col items-center gap-2">
                    <Building2 size={36} className="opacity-40 text-primary" />
                    <span className="text-xs font-medium">No Image Uploaded</span>
                  </div>
                )}
                {formData.category && (
                  <span className="absolute top-3 right-3 bg-primary text-primary-foreground text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full shadow-sm">
                    {formData.category}
                  </span>
                )}
              </div>

              {/* Preview Details */}
              <div className="p-4 space-y-3">
                <h3 className="font-serif text-lg font-bold text-foreground line-clamp-1">
                  {formData.name || "Grand Palace Ballroom"}
                </h3>

                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <MapPin size={14} className="text-primary/70 shrink-0" />
                  <span className="line-clamp-1">
                    {formData.location ? `${formData.location}` : "City Center, Kochi"}
                    {formData.address ? `, ${formData.address}` : ""}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 border-t border-border/30 pt-3">
                  <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                    <Users size={14} className="text-primary/70" />
                    <span>{formData.capacity ? `${formData.capacity} Guests` : "— Guests"}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                    <Clock size={14} className="text-primary/70" />
                    <span>{formData.bookingType ? `${formData.bookingType}` : "— Booking"}</span>
                  </div>
                </div>

                {amenities.length > 0 && (
                  <div className="border-t border-border/30 pt-3">
                    <div className="flex flex-wrap gap-1">
                      {amenities.slice(0, 3).map((item, idx) => (
                        <span key={idx} className="text-[10px] bg-primary/5 text-primary border border-primary/10 px-2 py-0.5 rounded-full">
                          {item}
                        </span>
                      ))}
                      {amenities.length > 3 && (
                        <span className="text-[10px] bg-secondary text-muted-foreground px-2 py-0.5 rounded-full">
                          +{amenities.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </motion.section>

          {/* Amenities Section */}
          <motion.section
            variants={cardVariants}
            className="rounded-2xl border border-border/60 bg-white/70 backdrop-blur-sm p-6 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="flex items-center gap-3 border-b border-border/40 pb-4 mb-4">
              <div className="p-2 rounded-xl bg-primary/10 text-primary">
                <Sparkles size={20} />
              </div>
              <div>
                <h2 className="font-semibold text-lg text-foreground">
                  Amenities
                </h2>
                <p className="text-xs text-muted-foreground">
                  List services like parking, catering, Wi-Fi, etc.
                </p>
              </div>
            </div>

            <div className="flex gap-2">
              <input
                type="text"
                className="input flex-1"
                placeholder="e.g., Free Wi-Fi"
                value={amenityInput}
                onChange={(e) => setAmenityInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && addAmenity()}
              />
              <button
                type="button"
                onClick={addAmenity}
                className="btn btn-primary px-3 cursor-pointer"
                title="Add Amenity"
              >
                <Plus size={18} />
              </button>
            </div>

            <div className="flex flex-wrap gap-1.5 mt-4 max-h-[160px] overflow-y-auto pr-1">
              <AnimatePresence>
                {amenities.map((item, index) => (
                  <motion.div
                    key={item + index}
                    initial={{ opacity: 0, scale: 0.85 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.85, transition: { duration: 0.15 } }}
                    layout
                    className="flex items-center gap-1.5 rounded-full bg-primary/5 border border-primary/10 px-3 py-1 text-xs font-semibold text-primary"
                  >
                    {item}
                    <button
                      type="button"
                      onClick={() => removeAmenity(index)}
                      className="text-primary/70 hover:text-primary hover:bg-primary/10 rounded-full p-0.5 transition-colors cursor-pointer"
                    >
                      <X size={12} />
                    </button>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
            {amenities.length === 0 && (
              <span className="text-xs text-muted-foreground/60 italic block mt-1">
                No amenities added yet.
              </span>
            )}
          </motion.section>

          {/* Venue Images Section */}
          <motion.section
            variants={cardVariants}
            className="rounded-2xl border border-border/60 bg-white/70 backdrop-blur-sm p-6 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="flex items-center gap-3 border-b border-border/40 pb-4 mb-4">
              <div className="p-2 rounded-xl bg-primary/10 text-primary">
                <ImageIcon size={20} />
              </div>
              <div>
                <h2 className="font-semibold text-lg text-foreground">
                  Venue Images
                </h2>
                <p className="text-xs text-muted-foreground">
                  Upload multiple photos of the interior/exterior.
                </p>
              </div>
            </div>

            {/* Drag & Drop Area */}
            <label
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-2xl p-6 flex flex-col items-center justify-center cursor-pointer transition-all duration-200 ${
                isDragging
                  ? "border-primary bg-primary/5 scale-[1.01]"
                  : "border-border hover:border-primary/60 hover:bg-secondary/40"
              }`}
            >
              <Upload size={32} className={`${isDragging ? "text-primary animate-bounce" : "text-muted-foreground/80"}`} />
              <span className="mt-3 text-sm font-semibold text-foreground">
                Drag & Drop Images
              </span>
              <span className="text-xs text-muted-foreground mt-1">
                or click to browse local files
              </span>
              <input
                type="file"
                multiple
                accept="image/*"
                hidden
                onChange={handleImages}
              />
            </label>

            {/* File List / Previews */}
            {images.length > 0 && (
              <div className="mt-5 space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                    Uploaded ({images.length})
                  </span>

                  <button
                    onClick={() => setImages([])}
                    className="text-[11px] font-bold text-accent hover:underline cursor-pointer"
                  >
                    Clear All
                  </button>
                </div>

                <div className="grid grid-cols-3 gap-2">
                  <AnimatePresence>
                    {images.map((image, idx) => (
                      <motion.div
                        key={image.public_id || idx}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                        className="relative aspect-square rounded-xl overflow-hidden border border-border group"
                      >
                        <img
                          src={image.image_url}
                          alt={`Upload ${idx}`}
                          className="w-full h-full object-cover"
                        />

                        {image.is_cover && (
                          <span className="absolute top-1 left-1 bg-primary text-white text-[10px] px-2 py-1 rounded">
                            Cover
                          </span>
                        )}

                        <button
                          type="button"
                          onClick={() => removeImage(idx)}
                          className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity text-white rounded-xl cursor-pointer"
                        >
                          <X size={16} />
                        </button>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                </div>
              </div>
            )}

            {images.length === 0 && (
              <p className="mt-3 text-xs text-muted-foreground/60 italic">
                No images selected yet.
              </p>
            )}
          {uploading && (
            <div className="mt-3 text-sm text-primary font-medium">
              Uploading images...
            </div>
          )}
          </motion.section>
        </div>
      </motion.div>

      {/* Footer Form Submission buttons */}
      <div className="flex items-center justify-end gap-3 mt-8 border-t border-border/40 pt-6">
        <button
          onClick={() => navigate(-1)}
          className="btn btn-outline"
        >
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
  )
}



// sample form object
// {
//     "name": "Godha",
//     "category": "Sports",
//     "location": "Trivandrum",
//     "address": "Kazhakkottam",
//     "description": "skfjasldjflsadflaskdjflskf",
//     "capacity": "50",
//     "bookingType": "Hourly",
//     "contactName": "owner",
//     "contactPhone": "9847987478",
//     "contactEmail": "booking@example.coma",
//     "amenities": [
//         "parking",
//         "water",
//         "dressing rooms"
//     ],
//     "images": [
//         {}
//     ]
// }

// will modify this to
// {
//     "name": "Godha",
//     "category_id": "Sports",
//     "location_id": "Trivandrum",
//     "address": "Kazhakkottam",
//     "description": "skfjasldjflsadflaskdjflskf",
//     "capacity": "50",
//     "bookingType_id": "Hourly",
//     "contactName": "owner",
//     "contactPhone": "9847987478",
//     "contactEmail": "booking@example.coma",
//     "amenities": [
//         "parking",
//         "water",
//         "dressing rooms"
//     ],
//     "images": [
//         {}
//     ]
// }


