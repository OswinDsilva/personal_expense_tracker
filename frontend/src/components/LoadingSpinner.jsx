import './LoadingSpinner.css';

export default function LoadingSpinner() {
  return (
    <div className="loading-spinner-container">
      <div className="spinner-text-with-dots">
        <h1 className="spinner-text">Spinning up the server</h1>
        <div className="spinner-dots">
          <span className="dot"></span>
          <span className="dot"></span>
          <span className="dot"></span>
        </div>
      </div>
    </div>
  );
}
