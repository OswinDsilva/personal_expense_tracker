import { useState, useEffect } from 'react';

export const useHealthCheck = () => {
  const [isHealthy, setIsHealthy] = useState(false);

  useEffect(() => {
    if (isHealthy) {
      return;
    }

    const checkHealth = async () => {
      try {
        const response = await fetch('/api/health');
        if (response.ok) {
          setIsHealthy(true);
        }
      } catch (error) {
        // backend not up yet, will retry
      }
    };

    checkHealth(); // check immediately
    const interval = setInterval(checkHealth, 2000);

    return () => clearInterval(interval); // cleanup
  }, [isHealthy]);

  return isHealthy;
};
