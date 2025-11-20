import './LoadingSkeleton.css';

export function MessageSkeleton() {
  return (
    <div className="skeleton-message">
      <div className="skeleton-avatar"></div>
      <div className="skeleton-content">
        <div className="skeleton-line skeleton-line-short"></div>
        <div className="skeleton-line"></div>
        <div className="skeleton-line skeleton-line-medium"></div>
      </div>
    </div>
  );
}

export function FlightSkeleton() {
  return (
    <div className="skeleton-card">
      <div className="skeleton-card-header">
        <div className="skeleton-line skeleton-line-short"></div>
        <div className="skeleton-circle"></div>
      </div>
      <div className="skeleton-card-body">
        <div className="skeleton-line"></div>
        <div className="skeleton-line skeleton-line-medium"></div>
      </div>
    </div>
  );
}

export function HotelSkeleton() {
  return (
    <div className="skeleton-card">
      <div className="skeleton-image"></div>
      <div className="skeleton-card-body">
        <div className="skeleton-line skeleton-line-short"></div>
        <div className="skeleton-line skeleton-line-medium"></div>
        <div className="skeleton-line"></div>
      </div>
    </div>
  );
}

export function SearchingSkeleton({ type = 'flight' }: { type?: 'flight' | 'hotel' }) {
  return (
    <div className="searching-skeleton">
      <div className="searching-icon">
        {type === 'flight' ? '✈️' : '🏨'}
      </div>
      <div className="searching-text">
        <div className="skeleton-line skeleton-line-medium"></div>
        <div className="skeleton-line skeleton-line-short"></div>
      </div>
      <div className="searching-dots">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  );
}
