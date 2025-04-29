document.addEventListener("DOMContentLoaded", function () {
    const timers = document.querySelectorAll('.countdown-timer');
  
    timers.forEach(function (timer) {
      const expiration = timer.dataset.expiration;
  
      if (expiration === "N/A") {
        timer.innerText = "N/A";
        return;
      }
  
      const expirationDate = new Date(expiration).getTime();
  
      function updateCountdown() {
        const now = new Date().getTime();
        const distance = expirationDate - now;
  
        if (distance <= 0) {
          timer.innerText = "Expired";
          return;
        }
  
        const hours = Math.floor((distance / (1000 * 60 * 60)) % 24);
        const minutes = Math.floor((distance / (1000 * 60)) % 60);
        const seconds = Math.floor((distance / 1000) % 60);
  
        timer.innerText =
          `${hours} hour${hours !== 1 ? 's' : ''} ` +
          `${minutes} minute${minutes !== 1 ? 's' : ''} ` +
          `${seconds} second${seconds !== 1 ? 's' : ''}`;
      }
  
      updateCountdown();
      setInterval(updateCountdown, 1000);
    });
  });
  