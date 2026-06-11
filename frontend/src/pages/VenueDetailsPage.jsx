import { useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { motion } from "framer-motion"
import { Star, MapPin, Users, DollarSign, Clock, Phone, Mail, ChevronLeft, Heart, Share2, Check } from "lucide-react"
import { getRelatedVenues, getVenueById } from "../apis/venues"
import Reveal from "../components/common/Reveal"
import MainLayout from "../layouts/MainLayout"

export default function VenueDetailsPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const venue = getVenueById(id)
  const [currentImageIndex, setCurrentImageIndex] = useState(0)
  const [isSaved, setIsSaved] = useState(false)
  const [activeTab, setActiveTab] = useState("overview")

  if (!venue) {
    return (
      <MainLayout>
        <div className="container mx-auto px-4 py-20 text-center">
          <h1 className="text-3xl font-serif font-bold mb-4">Venue not found</h1>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition"
          >
            Back to home
          </button>
        </div>
      </MainLayout>
    )
  }

  const relatedVenues = getRelatedVenues(venue)

  const nextImage = () => {
    setCurrentImageIndex((prev) => (prev + 1) % venue.gallery.length)
  }

  const prevImage = () => {
    setCurrentImageIndex((prev) => (prev - 1 + venue.gallery.length) % venue.gallery.length)
  }

  return (
    <MainLayout>
      <main className="pt-8">
        {/* Breadcrumb & Header */}
        <div className="container mx-auto px-4 mb-8">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-primary hover:underline mb-6 transition"
          >
            <ChevronLeft size={20} />
            Back to venues
          </button>

          <div className="flex justify-between items-start mb-6">
            <div>
              <h1 className="text-4xl font-serif font-bold mb-2">{venue.name}</h1>
              <div className="flex items-center gap-4 flex-wrap">
                <div className="flex items-center gap-1">
                  <Star size={18} fill="currentColor" className="text-accent" />
                  <span className="font-semibold">{venue.rating}</span>
                  <span className="text-muted-foreground">({venue.reviews} reviews)</span>
                </div>
                <div className="flex items-center gap-1 text-muted-foreground">
                  <MapPin size={18} />
                  {venue.location}
                </div>
              </div>
            </div>
            <div className="flex gap-3">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsSaved(!isSaved)}
                className={`p-3 rounded-full border transition ${
                  isSaved ? 'bg-accent text-accent-foreground' : 'border-border hover:bg-muted'
                }`}
              >
                <Heart size={20} fill={isSaved ? 'currentColor' : 'none'} />
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="p-3 rounded-full border border-border hover:bg-muted transition"
              >
                <Share2 size={20} />
              </motion.button>
            </div>
          </div>
        </div>

        {/* Gallery */}
        <Reveal>
          <div className="container mx-auto px-4 mb-12">
            <div className="relative rounded-2xl overflow-hidden bg-muted h-96 md:h-[500px]">
              <motion.img
                key={currentImageIndex}
                src={venue.gallery[currentImageIndex]}
                alt={`${venue.name} view ${currentImageIndex + 1}`}
                className="w-full h-full object-cover"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.5 }}
              />
              
              {/* Navigation buttons */}
              <button
                onClick={prevImage}
                className="absolute left-4 top-1/2 -translate-y-1/2 bg-background/80 hover:bg-background p-2 rounded-full transition z-10"
              >
                <ChevronLeft size={24} />
              </button>
              <button
                onClick={nextImage}
                className="absolute right-4 top-1/2 -translate-y-1/2 bg-background/80 hover:bg-background p-2 rounded-full transition z-10"
              >
                <ChevronLeft size={24} className="rotate-180" />
              </button>

              {/* Image counter */}
              <div className="absolute bottom-4 right-4 bg-background/80 px-4 py-2 rounded-full text-sm font-semibold">
                {currentImageIndex + 1} / {venue.gallery.length}
              </div>
            </div>

            {/* Thumbnail gallery */}
            <div className="flex gap-3 mt-4">
              {venue.gallery.map((img, idx) => (
                <motion.button
                  key={idx}
                  onClick={() => setCurrentImageIndex(idx)}
                  whileHover={{ scale: 1.05 }}
                  className={`w-20 h-20 rounded-lg overflow-hidden border-2 transition ${
                    idx === currentImageIndex ? "border-primary" : "border-muted"
                  }`}
                >
                  <img src={img} alt={`Thumbnail ${idx + 1}`} className="w-full h-full object-cover" />
                </motion.button>
              ))}
            </div>
          </div>
        </Reveal>

        {/* Main content */}
        <div className="container mx-auto px-4 mb-16">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left column - Details */}
            <div className="lg:col-span-2">
              {/* Quick info cards */}
              <Reveal>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                  <motion.div
                    whileHover={{ translateY: -4 }}
                    className="bg-card border border-border rounded-xl p-4 text-center"
                  >
                    <Users size={24} className="mx-auto mb-2 text-primary" />
                    <p className="text-sm text-muted-foreground">Capacity</p>
                    <p className="font-bold text-lg">{venue.capacity}</p>
                  </motion.div>
                  <motion.div
                    whileHover={{ translateY: -4 }}
                    className="bg-card border border-border rounded-xl p-4 text-center"
                  >
                    <DollarSign size={24} className="mx-auto mb-2 text-primary" />
                    <p className="text-sm text-muted-foreground">Price</p>
                    <p className="font-bold text-lg">{venue.price}</p>
                  </motion.div>
                  <motion.div
                    whileHover={{ translateY: -4 }}
                    className="bg-card border border-border rounded-xl p-4 text-center"
                  >
                    <Clock size={24} className="mx-auto mb-2 text-primary" />
                    <p className="text-sm text-muted-foreground">Hours</p>
                    <p className="font-bold text-sm">{venue.hours}</p>
                  </motion.div>
                  <motion.div
                    whileHover={{ translateY: -4 }}
                    className="bg-card border border-border rounded-xl p-4 text-center"
                  >
                    <MapPin size={24} className="mx-auto mb-2 text-primary" />
                    <p className="text-sm text-muted-foreground">Type</p>
                    <p className="font-bold text-sm">{venue.type}</p>
                  </motion.div>
                </div>
              </Reveal>

              {/* Tabs */}
              <Reveal>
                <div className="flex border-b border-border mb-8">
                  {["overview", "amenities", "reviews"].map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`px-6 py-4 font-semibold capitalize transition border-b-2 ${
                        activeTab === tab
                          ? 'text-primary border-primary'
                          : 'text-muted-foreground border-transparent hover:text-foreground'
                      }`}
                    >
                      {tab}
                    </button>
                  ))}
                </div>
              </Reveal>

              {/* Tab content */}
              {activeTab === "overview" && (
                <Reveal>
                  <div className="space-y-8">
                    <div>
                      <h2 className="text-2xl font-serif font-bold mb-4">About this venue</h2>
                      <p className="text-foreground/90 leading-relaxed mb-6">{venue.description}</p>
                      
                      <div className="grid grid-cols-2 gap-4 mb-6">
                        {venue.highlights.map((highlight, idx) => (
                          <div key={idx} className="flex items-center gap-2">
                            <Check size={20} className="text-primary flex-shrink-0" />
                            <span className="text-sm">{highlight}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h3 className="text-xl font-serif font-bold mb-4">Event Details</h3>
                      <div className="space-y-3">
                        <p><span className="font-semibold">Guest Range:</span> {venue.minEventSize} - {venue.maxEventSize} guests</p>
                        <p><span className="font-semibold">Price per Person:</span> {`$${venue.pricePerPerson}`}</p>
                        <p><span className="font-semibold">Parking:</span> {venue.parking}</p>
                        <div>
                          <span className="font-semibold block mb-2">Event Types Hosted:</span>
                          <div className="flex flex-wrap gap-2">
                            {venue.eventTypes.map((type, idx) => (
                              <span key={idx} className="px-3 py-1 bg-secondary text-secondary-foreground rounded-full text-sm">
                                {type}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h3 className="text-xl font-serif font-bold mb-4">Location</h3>
                      <p className="mb-2 flex items-center gap-2">
                        <MapPin size={18} className="text-primary" />
                        {venue.address}
                      </p>
                      <div className="bg-muted rounded-lg h-64 mt-4 flex items-center justify-center text-muted-foreground">
                        Map view coming soon
                      </div>
                    </div>
                  </div>
                </Reveal>
              )}

              {activeTab === "amenities" && (
                <Reveal>
                  <div>
                    <h2 className="text-2xl font-serif font-bold mb-6">Amenities & Features</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {venue.amenities.map((amenity, idx) => (
                        <motion.div
                          key={idx}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: idx * 0.05 }}
                          className="flex items-center gap-3 p-4 bg-card border border-border rounded-lg"
                        >
                          <Check size={20} className="text-primary flex-shrink-0" />
                          <span>{amenity}</span>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                </Reveal>
              )}

              {activeTab === "reviews" && (
                <Reveal>
                  <div>
                    <h2 className="text-2xl font-serif font-bold mb-6">Guest Reviews</h2>
                    <div className="space-y-4">
                      {venue.reviews_list.map((review, idx) => (
                        <motion.div
                          key={idx}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: idx * 0.1 }}
                          className="bg-card border border-border rounded-lg p-6"
                        >
                          <div className="flex justify-between items-start mb-3">
                            <div>
                              <h4 className="font-semibold">{review.name}</h4>
                              <p className="text-sm text-muted-foreground">{review.date}</p>
                            </div>
                            <div className="flex gap-1">
                              {[...Array(review.rating)].map((_, i) => (
                                <Star key={i} size={16} fill="currentColor" className="text-accent" />
                              ))}
                            </div>
                          </div>
                          <p className="text-foreground/90">{review.text}</p>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                </Reveal>
              )}
            </div>

            {/* Right column - Booking sidebar */}
            <Reveal>
              <div className="lg:col-span-1">
                <div className="bg-card border border-border rounded-2xl p-8 sticky top-24">
                  {/* Price section */}
                  <div className="mb-8">
                    <p className="text-sm text-muted-foreground mb-2">Starting from</p>
                    <p className="text-4xl font-serif font-bold mb-1">{venue.price}</p>
                    <p className="text-sm text-muted-foreground">{`$${venue.pricePerPerson}`} per person</p>
                  </div>

                  {/* Booking buttons */}
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="w-full bg-primary text-primary-foreground py-3 rounded-lg font-semibold mb-3 hover:opacity-90 transition"
                  >
                    Book Now
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="w-full border-2 border-primary text-primary py-3 rounded-lg font-semibold hover:bg-primary/5 transition"
                  >
                    Inquiry
                  </motion.button>

                  {/* Contact info */}
                  <div className="border-t border-border mt-8 pt-8">
                    <h3 className="font-serif font-bold text-lg mb-4">Contact Venue</h3>
                    <div className="space-y-3">
                      <div className="flex items-center gap-3">
                        <Phone size={18} className="text-primary flex-shrink-0" />
                        <a href={`tel:${venue.phone}`} className="text-primary hover:underline text-sm">
                          {venue.phone}
                        </a>
                      </div>
                      <div className="flex items-center gap-3">
                        <Mail size={18} className="text-primary flex-shrink-0" />
                        <a href={`mailto:${venue.email}`} className="text-primary hover:underline text-sm break-all">
                          {venue.email}
                        </a>
                      </div>
                    </div>
                  </div>

                  {/* Venue owner */}
                  <div className="border-t border-border mt-8 pt-8">
                    <h3 className="font-serif font-bold text-lg mb-4">Venue Manager</h3>
                    <div className="flex items-center gap-3">
                      <img
                        src={venue.ownerImage}
                        alt={venue.owner}
                        className="w-12 h-12 rounded-full object-cover"
                      />
                      <div>
                        <p className="font-semibold text-sm">{venue.owner}</p>
                        <p className="text-xs text-muted-foreground">Verified host</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </Reveal>
          </div>
        </div>

        {/* Related venues */}
        {relatedVenues.length > 0 && (
          <Reveal>
            <section className="container mx-auto px-4 py-16 border-t border-border">
              <h2 className="text-3xl font-serif font-bold mb-8">Similar venues</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {relatedVenues.map((relatedVenue) => (
                  <motion.div
                    key={relatedVenue.id}
                    whileHover={{ translateY: -8 }}
                    onClick={() => navigate(`/venue/${relatedVenue.id}`)}
                    className="cursor-pointer group"
                  >
                    <div className="relative h-64 rounded-xl overflow-hidden bg-muted mb-4">
                      <img
                        src={relatedVenue.image}
                        alt={relatedVenue.name}
                        className="w-full h-full object-cover group-hover:scale-110 transition duration-300"
                      />
                      <div className="absolute top-3 right-3 bg-background/80 backdrop-blur px-3 py-1 rounded-full text-sm font-semibold flex items-center gap-1">
                        <Star size={14} fill="currentColor" className="text-accent" />
                        {relatedVenue.rating}
                      </div>
                    </div>
                    <h3 className="font-serif font-bold text-lg mb-1 group-hover:text-primary transition">
                      {relatedVenue.name}
                    </h3>
                    <p className="text-sm text-muted-foreground mb-3 flex items-center gap-1">
                      <MapPin size={14} />
                      {relatedVenue.location}
                    </p>
                    <p className="font-semibold text-primary">{relatedVenue.price}</p>
                  </motion.div>
                ))}
              </div>
            </section>
          </Reveal>
        )}
      </main>

    </MainLayout>
  )
}
