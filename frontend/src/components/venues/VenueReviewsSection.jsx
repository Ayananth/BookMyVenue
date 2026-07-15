import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { Star } from "lucide-react"
import {
  createVenueReview,
  fetchVenueReviews,
  parseReviewError,
  reviewItemFromApi,
} from "../../apis/reviews"
import { useAuth } from "../../contexts/AuthContext"
import { useAuthModal } from "../../contexts/AuthModalContext"

const STAR_VALUES = [1, 2, 3, 4, 5]

function StarRatingDisplay({ rating, size = 16 }) {
  const filled = Math.round(Number(rating) || 0)
  return (
    <div className="flex gap-0.5" aria-label={`${filled} out of 5 stars`}>
      {STAR_VALUES.map((value) => (
        <Star
          key={value}
          size={size}
          fill={value <= filled ? "currentColor" : "none"}
          className={value <= filled ? "text-accent" : "text-muted-foreground/40"}
        />
      ))}
    </div>
  )
}

function StarRatingInput({ value, onChange, disabled = false }) {
  const [hovered, setHovered] = useState(0)
  const active = hovered || value

  return (
    <div
      className="flex gap-1"
      role="radiogroup"
      aria-label="Your rating"
      onMouseLeave={() => setHovered(0)}
    >
      {STAR_VALUES.map((star) => {
        const isActive = star <= active
        return (
          <button
            key={star}
            type="button"
            role="radio"
            aria-checked={value === star}
            aria-label={`${star} star${star === 1 ? "" : "s"}`}
            disabled={disabled}
            onMouseEnter={() => setHovered(star)}
            onFocus={() => setHovered(star)}
            onBlur={() => setHovered(0)}
            onClick={() => onChange(star)}
            className="rounded p-0.5 transition hover:scale-110 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <Star
              size={28}
              fill={isActive ? "currentColor" : "none"}
              className={isActive ? "text-accent" : "text-muted-foreground/40"}
            />
          </button>
        )
      })}
    </div>
  )
}

function RatingSummary({ averageRating, totalCount, items }) {
  const distribution = STAR_VALUES.map((star) => {
    const count = items.filter((item) => item.rating === star).length
    const percent = totalCount > 0 ? Math.round((count / totalCount) * 100) : 0
    return { star, count, percent }
  }).reverse()

  return (
    <div className="mb-8 grid gap-6 rounded-xl border border-border bg-card p-6 sm:grid-cols-[auto_1fr] sm:items-center">
      <div className="text-center sm:pr-6 sm:border-r sm:border-border">
        <p className="font-serif text-4xl font-bold">
          {averageRating != null ? averageRating.toFixed(1) : "—"}
        </p>
        <div className="mt-2 flex justify-center">
          <StarRatingDisplay rating={averageRating ?? 0} size={18} />
        </div>
        <p className="mt-2 text-sm text-muted-foreground">
          {totalCount} {totalCount === 1 ? "rating" : "ratings"}
        </p>
      </div>

      <div className="space-y-2">
        {distribution.map(({ star, percent }) => (
          <div key={star} className="flex items-center gap-3 text-sm">
            <span className="w-8 text-muted-foreground">{star}★</span>
            <div className="h-2 flex-1 overflow-hidden rounded-full bg-muted">
              <div
                className="h-full rounded-full bg-accent transition-all"
                style={{ width: `${percent}%` }}
              />
            </div>
            <span className="w-10 text-right text-muted-foreground">{percent}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function ReviewCard({ review, index }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="rounded-xl border border-border bg-card p-5 sm:p-6"
    >
      <div className="mb-3 flex items-start justify-between gap-3">
        <div>
          <h4 className="font-semibold">
            {review.name}
            {review.isOwn ? (
              <span className="ml-2 text-xs font-medium text-primary">(You)</span>
            ) : null}
          </h4>
          <p className="text-sm text-muted-foreground">
            {review.date}
            {review.isEdited ? " · Edited" : ""}
          </p>
        </div>
        <StarRatingDisplay rating={review.rating} />
      </div>
      {review.title ? (
        <p className="mb-1 font-medium text-foreground">{review.title}</p>
      ) : null}
      {review.text ? (
        <p className="text-foreground/90 leading-relaxed">{review.text}</p>
      ) : (
        <p className="text-sm italic text-muted-foreground">Rated without a written review.</p>
      )}
    </motion.div>
  )
}

export default function VenueReviewsSection({
  venueId,
  fallbackRating = null,
  fallbackReviewCount = 0,
  fallbackReviews = [],
  onStatsChange,
}) {
  const { user, isAuthenticated } = useAuth()
  const { openAuthModal } = useAuthModal()

  const [loading, setLoading] = useState(Boolean(venueId))
  const [error, setError] = useState("")
  const [averageRating, setAverageRating] = useState(fallbackRating)
  const [totalCount, setTotalCount] = useState(fallbackReviewCount)
  const [reviews, setReviews] = useState([])

  const [rating, setRating] = useState(0)
  const [title, setTitle] = useState("")
  const [reviewText, setReviewText] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState("")
  const [submitSuccess, setSubmitSuccess] = useState("")

  const currentUserId = user?.id ?? null
  const currentUserName = user?.full_name || user?.name || "You"

  const ownReview = reviews.find((item) => item.isOwn) ?? null

  const loadReviews = async () => {
    if (!venueId) {
      const mapped = fallbackReviews.map((item, index) => ({
        ratingId: `fallback-${index}`,
        userId: null,
        rating: item.rating,
        reviewId: null,
        title: item.title ?? null,
        text: item.text ?? null,
        isEdited: false,
        createdAt: null,
        date: item.date ?? "",
        name: item.name ?? "Guest",
        isOwn: false,
      }))
      setReviews(mapped)
      setAverageRating(fallbackRating)
      setTotalCount(fallbackReviewCount || mapped.length)
      setLoading(false)
      return
    }

    setLoading(true)
    setError("")

    try {
      const data = await fetchVenueReviews(venueId)
      const mapped = (data.items ?? []).map((item) =>
        reviewItemFromApi(item, {
          currentUserId,
          currentUserName,
        }),
      )
      setReviews(mapped)
      setAverageRating(data.average_rating)
      setTotalCount(data.total_count ?? mapped.length)
      onStatsChange?.({
        rating: data.average_rating,
        reviews: data.total_count ?? mapped.length,
      })
    } catch (err) {
      console.error("Failed to load reviews:", err)
      setError(parseReviewError(err))
      const mapped = fallbackReviews.map((item, index) => ({
        ratingId: `fallback-${index}`,
        userId: null,
        rating: item.rating,
        reviewId: null,
        title: item.title ?? null,
        text: item.text ?? null,
        isEdited: false,
        createdAt: null,
        date: item.date ?? "",
        name: item.name ?? "Guest",
        isOwn: false,
      }))
      if (mapped.length) {
        setReviews(mapped)
        setAverageRating(fallbackRating)
        setTotalCount(fallbackReviewCount || mapped.length)
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadReviews()
    // eslint-disable-next-line react-hooks/exhaustive-deps -- reload when venue or user changes
  }, [venueId, currentUserId])

  const resetForm = () => {
    setRating(0)
    setTitle("")
    setReviewText("")
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSubmitError("")
    setSubmitSuccess("")

    if (!isAuthenticated) {
      openAuthModal({
        message: "Sign in to rate this venue.",
        onSuccess: () => {},
      })
      return
    }

    if (!venueId) {
      setSubmitError("This venue cannot accept ratings yet.")
      return
    }

    if (rating < 1 || rating > 5) {
      setSubmitError("Please choose a rating from 1 to 5 stars.")
      return
    }

    if (title.trim() && !reviewText.trim()) {
      setSubmitError("Add a short review when including a title.")
      return
    }

    setSubmitting(true)
    try {
      await createVenueReview(venueId, {
        rating,
        title,
        review: reviewText,
      })
      setSubmitSuccess("Thanks! Your rating has been submitted.")
      resetForm()
      await loadReviews()
    } catch (err) {
      setSubmitError(parseReviewError(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div>
      <h2 className="mb-6 font-serif text-2xl font-bold">Guest Reviews</h2>

      {loading ? (
        <p className="mb-8 text-muted-foreground">Loading reviews...</p>
      ) : (
        <RatingSummary
          averageRating={averageRating}
          totalCount={totalCount}
          items={reviews}
        />
      )}

      {error && !reviews.length ? (
        <p className="mb-6 text-sm text-red-700">{error}</p>
      ) : null}

      {!ownReview ? (
        <form
          onSubmit={handleSubmit}
          className="mb-8 rounded-xl border border-border bg-card p-5 sm:p-6"
        >
          <h3 className="mb-1 font-serif text-lg font-bold">Rate this venue</h3>
          <p className="mb-4 text-sm text-muted-foreground">
            Share a 1–5 star rating. A written review is optional.
          </p>

          <div className="mb-4">
            <StarRatingInput
              value={rating}
              onChange={setRating}
              disabled={submitting}
            />
            {rating > 0 ? (
              <p className="mt-2 text-sm text-muted-foreground">
                You selected {rating} of 5 stars
              </p>
            ) : null}
          </div>

          <div className="mb-3">
            <label htmlFor="review-title" className="mb-1.5 block text-sm font-medium">
              Title <span className="font-normal text-muted-foreground">(optional)</span>
            </label>
            <input
              id="review-title"
              type="text"
              maxLength={150}
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              disabled={submitting}
              placeholder="Sum up your experience"
              className="input"
            />
          </div>

          <div className="mb-4">
            <label htmlFor="review-text" className="mb-1.5 block text-sm font-medium">
              Review <span className="font-normal text-muted-foreground">(optional)</span>
            </label>
            <textarea
              id="review-text"
              rows={4}
              value={reviewText}
              onChange={(event) => setReviewText(event.target.value)}
              disabled={submitting}
              placeholder="What stood out about this venue?"
              className="input min-h-[110px] resize-y"
            />
          </div>

          {submitError ? (
            <p className="mb-3 text-sm text-red-700">{submitError}</p>
          ) : null}
          {submitSuccess ? (
            <p className="mb-3 text-sm text-primary">{submitSuccess}</p>
          ) : null}

          <button
            type="submit"
            disabled={submitting || rating < 1}
            className="btn btn-primary"
          >
            {submitting ? "Submitting..." : isAuthenticated ? "Submit rating" : "Sign in to rate"}
          </button>
        </form>
      ) : (
        <div className="mb-8 rounded-xl border border-primary/30 bg-primary/5 p-5 sm:p-6">
          <p className="text-sm font-medium text-foreground">
            You rated this venue {ownReview.rating} of 5 stars
            {ownReview.date ? ` on ${ownReview.date}` : ""}.
          </p>
          <p className="mt-1 text-sm text-muted-foreground">
            Your rating appears in the list below.
          </p>
        </div>
      )}

      {loading ? null : reviews.length > 0 ? (
        <div className="space-y-4">
          {reviews.map((review, index) => (
            <ReviewCard key={review.ratingId} review={review} index={index} />
          ))}
        </div>
      ) : (
        <p className="text-muted-foreground">
          No reviews yet. Be the first to rate this venue.
        </p>
      )}
    </div>
  )
}
