// Desktop buttons
const container = document.getElementById('container');
const signUpDesktopButton = document.getElementById('signUpDesktop');
const signInDesktopButton = document.getElementById('signInDesktop');

if (signUpDesktopButton && signInDesktopButton && container) {
  signUpDesktopButton.addEventListener('click', () => {
    container.classList.add("right-panel-active");
    container.classList.remove("mobile-sign-up-active");
  });

  signInDesktopButton.addEventListener('click', () => {
    container.classList.remove("right-panel-active");
    container.classList.remove("mobile-sign-up-active");
  });
}

// Mobile buttons
const signUpMobileButton = document.getElementById('signUpMobile');
const signInMobileButton = document.getElementById('signInMobile');

if (signUpMobileButton && signInMobileButton && container) {
  function updateMobileButtons(activeButton) {
    signInMobileButton.classList.remove('mobile-active');
    signUpMobileButton.classList.remove('mobile-active');
    activeButton.classList.add('mobile-active');
  }

  signUpMobileButton.addEventListener('click', () => {
    if (window.innerWidth <= 778) {
      container.classList.add("mobile-sign-up-active");
      updateMobileButtons(signUpMobileButton);
    }
  });

  signInMobileButton.addEventListener('click', () => {
    if (window.innerWidth <= 778) {
      container.classList.remove("mobile-sign-up-active");
      updateMobileButtons(signInMobileButton);
    }
  });
}

// Navbar toggle for mobile (safe check)
const menuToggle = document.getElementById('menuToggle');
const menuList = document.getElementById('menuList');

if (menuToggle && menuList) {
  menuToggle.addEventListener('click', () => {
    menuList.classList.toggle('active');
  });
}
