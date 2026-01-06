/**
* Template Name: OnePage
* Updated: Mar 10 2023 with Bootstrap v5.2.3
* Template URL: https://bootstrapmade.com/onepage-multipurpose-bootstrap-template/
* Author: BootstrapMade.com
* License: https://bootstrapmade.com/license/
*/
(function() {
  "use strict";
  
  // Prevent multiple initializations
  if (window.mainJSInitialized) {
    return;
  }
  window.mainJSInitialized = true;

  /**
   * Easy selector helper function
   */
  const select = (el, all = false) => {
    if (!el) return null;
    try {
      el = el.trim();
      if (all) {
        return [...document.querySelectorAll(el)];
      } else {
        return document.querySelector(el);
      }
    } catch (e) {
      console.error('Error in select function:', e);
      return null;
    }
  }

  /**
   * Easy event listener function
   */
  const on = (type, el, listener, all = false) => {
    let selectEl = select(el, all)
    if (selectEl) {
      if (all) {
        selectEl.forEach(e => e.addEventListener(type, listener))
      } else {
        selectEl.addEventListener(type, listener)
      }
    }
  }

  /**
   * Easy on scroll event listener 
   */
  const onscroll = (el, listener) => {
    if (el && typeof listener === 'function') {
      try {
        el.addEventListener('scroll', listener);
      } catch (e) {
        console.error('Error adding scroll listener:', e);
      }
    }
  }

  /**
   * Navbar links active state on scroll
   */
  let navbarlinks = select('#navbar .scrollto', true)
  if (navbarlinks && navbarlinks.length > 0) {
    const navbarlinksActive = () => {
      try {
        let position = window.scrollY + 200
        navbarlinks.forEach(navbarlink => {
          if (!navbarlink || !navbarlink.hash) return
          let section = select(navbarlink.hash)
          if (!section) return
          if (position >= section.offsetTop && position <= (section.offsetTop + section.offsetHeight)) {
            navbarlink.classList.add('active')
          } else {
            navbarlink.classList.remove('active')
          }
        })
      } catch (e) {
        console.error('Error in navbarlinksActive:', e);
      }
    }
    window.addEventListener('load', navbarlinksActive)
    onscroll(document, navbarlinksActive)
  }

  /**
   * Scrolls to an element with header offset
   */
  const scrollto = (el) => {
    try {
      let header = select('#header')
      if (!header) return;
      let offset = header.offsetHeight || 0

      let targetElement = select(el)
      if (!targetElement) return;
      
      let elementPos = targetElement.offsetTop
      window.scrollTo({
        top: elementPos - offset,
        behavior: 'smooth'
      })
    } catch (e) {
      console.error('Error in scrollto:', e);
    }
  }

  /**
   * Toggle .header-scrolled class to #header when page is scrolled
   */
  let selectHeader = select('#header')
  if (selectHeader) {
    const headerScrolled = () => {
      if (window.scrollY > 100) {
        selectHeader.classList.add('header-scrolled')
      } else {
        selectHeader.classList.remove('header-scrolled')
      }
    }
    window.addEventListener('load', headerScrolled)
    onscroll(document, headerScrolled)
  }

  /**
   * Back to top button
   */
  let backtotop = select('.back-to-top')
  if (backtotop) {
    const toggleBacktotop = () => {
      if (window.scrollY > 100) {
        backtotop.classList.add('active')
      } else {
        backtotop.classList.remove('active')
      }
    }
    window.addEventListener('load', toggleBacktotop)
    onscroll(document, toggleBacktotop)
  }

  /**
   * Mobile nav toggle
   */
  on('click', '.mobile-nav-toggle', function(e) {
    try {
      const navbar = select('#navbar');
      const body = document.body;
      
      if (navbar) {
        const isMobile = navbar.classList.contains('navbar-mobile');
        
        if (isMobile) {
          // Закрываем меню
          navbar.classList.remove('navbar-mobile');
          body.style.overflow = '';
          body.style.position = '';
        } else {
          // Открываем меню
          navbar.classList.add('navbar-mobile');
          body.style.overflow = 'hidden';
          body.style.position = 'fixed';
          body.style.width = '100%';
        }
      }
      
      if (this) {
        this.classList.toggle('bi-list');
        this.classList.toggle('bi-x');
      }
    } catch (e) {
      console.error('Error in mobile nav toggle:', e);
    }
  })

  /**
   * Mobile nav dropdowns activate
   */
  on('click', '.navbar .dropdown > a', function(e) {
    try {
      const navbar = select('#navbar');
      if (navbar && navbar.classList.contains('navbar-mobile')) {
        e.preventDefault();
        if (this && this.nextElementSibling) {
          this.nextElementSibling.classList.toggle('dropdown-active');
        }
      }
    } catch (e) {
      console.error('Error in mobile nav dropdown:', e);
    }
  }, true)

  /**
   * Scrool with ofset on links with a class name .scrollto
   */
  on('click', '.scrollto', function(e) {
    try {
      if (this && this.hash && select(this.hash)) {
        e.preventDefault();

        let navbar = select('#navbar');
        const body = document.body;
        if (navbar && navbar.classList.contains('navbar-mobile')) {
          navbar.classList.remove('navbar-mobile');
          body.style.overflow = '';
          body.style.position = '';
          body.style.width = '';
          let navbarToggle = select('.mobile-nav-toggle');
          if (navbarToggle) {
            navbarToggle.classList.toggle('bi-list');
            navbarToggle.classList.toggle('bi-x');
          }
        }
        scrollto(this.hash);
      }
    } catch (e) {
      console.error('Error in scrollto handler:', e);
    }
  }, true)

  /**
   * Scroll with ofset on page load with hash links in the url
   */
  window.addEventListener('load', () => {
    try {
      if (window.location.hash) {
        const hashElement = select(window.location.hash);
        if (hashElement) {
          setTimeout(() => {
            scrollto(window.location.hash);
          }, 100);
        }
      }
    } catch (e) {
      console.error('Error scrolling to hash:', e);
    }
  });

  /**
   * Preloader
   */
  const removePreloader = () => {
    try {
      const preloader = document.getElementById('preloader');
      if (preloader) {
        // Add fade out class first
        preloader.classList.add('hidden');
        // Then remove after animation
        setTimeout(() => {
          if (preloader && preloader.parentNode) {
            preloader.remove();
          } else if (preloader) {
            preloader.style.display = 'none';
            preloader.style.opacity = '0';
            preloader.style.visibility = 'hidden';
          }
        }, 500);
      }
    } catch (e) {
      console.error('Error removing preloader:', e);
      const preloader = document.getElementById('preloader');
      if (preloader) {
        preloader.style.display = 'none';
        preloader.style.opacity = '0';
        preloader.style.visibility = 'hidden';
      }
    }
  };
  
  // Remove preloader when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      setTimeout(removePreloader, 100);
    });
    window.addEventListener('load', () => {
      setTimeout(removePreloader, 100);
    });
  } else {
    // DOM already loaded
    setTimeout(removePreloader, 100);
  }
  
  // Fallback: force remove after timeout (max 2 seconds)
  setTimeout(removePreloader, 2000);

  /**
   * Initiate glightbox 
   */
  if (typeof GLightbox !== 'undefined') {
    try {
      const glightbox = GLightbox({
        selector: '.glightbox'
      });
    } catch (e) {
      console.error('Error initializing glightbox:', e);
    }
  }

  /**
   * Testimonials slider
   */
  if (typeof Swiper !== 'undefined') {
    try {
      const testimonialsSlider = select('.testimonials-slider');
      if (testimonialsSlider) {
        new Swiper('.testimonials-slider', {
          speed: 600,
          loop: true,
          autoplay: {
            delay: 5000,
            disableOnInteraction: false
          },
          slidesPerView: 'auto',
          pagination: {
            el: '.swiper-pagination',
            type: 'bullets',
            clickable: true
          },
          breakpoints: {
            320: {
              slidesPerView: 1,
              spaceBetween: 20
            },

            1200: {
              slidesPerView: 3,
              spaceBetween: 20
            }
          }
        });
      }
    } catch (e) {
      console.error('Error initializing testimonials slider:', e);
    }
  }

  /**
   * Porfolio isotope and filter
   */
  window.addEventListener('load', () => {
    if (typeof Isotope !== 'undefined') {
      try {
        let portfolioContainer = select('.portfolio-container');
        if (portfolioContainer) {
          let portfolioIsotope = new Isotope(portfolioContainer, {
            itemSelector: '.portfolio-item'
          });

          let portfolioFilters = select('#portfolio-flters li', true);

          on('click', '#portfolio-flters li', function(e) {
            e.preventDefault();
            portfolioFilters.forEach(function(el) {
              el.classList.remove('filter-active');
            });
            this.classList.add('filter-active');

            portfolioIsotope.arrange({
              filter: this.getAttribute('data-filter')
            });
            if (typeof AOS !== 'undefined') {
              portfolioIsotope.on('arrangeComplete', function() {
                AOS.refresh()
              });
            }
          }, true);
        }
      } catch (e) {
        console.error('Error initializing portfolio isotope:', e);
      }
    }
  });

  /**
   * Initiate portfolio lightbox 
   */
  if (typeof GLightbox !== 'undefined') {
    try {
      const portfolioLightbox = GLightbox({
        selector: '.portfolio-lightbox'
      });
    } catch (e) {
      console.error('Error initializing portfolio lightbox:', e);
    }
  }

  /**
   * Portfolio details slider
   */
  if (typeof Swiper !== 'undefined') {
    try {
      const portfolioDetailsSlider = select('.portfolio-details-slider');
      if (portfolioDetailsSlider) {
        new Swiper('.portfolio-details-slider', {
          speed: 400,
          loop: true,
          autoplay: {
            delay: 5000,
            disableOnInteraction: false
          },
          pagination: {
            el: '.swiper-pagination',
            type: 'bullets',
            clickable: true
          }
        });
      }
    } catch (e) {
      console.error('Error initializing portfolio details slider:', e);
    }
  }

  /**
   * Animation on scroll
   */
  window.addEventListener('load', () => {
    if (typeof AOS !== 'undefined') {
      try {
        AOS.init({
          duration: 1000,
          easing: 'ease-in-out',
          once: true,
          mirror: false
        });
      } catch (e) {
        console.error('Error initializing AOS:', e);
      }
    }
  });

  /**
   * Initiate Pure Counter 
   */
  if (typeof PureCounter !== 'undefined') {
    try {
      new PureCounter();
    } catch (e) {
      console.error('Error initializing PureCounter:', e);
    }
  }

  /**
   * Modern Banner Slider - Bootstrap Carousel with animations
   */
  const modernBannerCarousel = document.getElementById('modernBannerCarousel');
  if (modernBannerCarousel) {
    // Reset animations when slide changes
    modernBannerCarousel.addEventListener('slide.bs.carousel', function (e) {
      const currentSlide = e.relatedTarget;
      const slideTextWrapper = currentSlide.querySelector('.slide-text-wrapper');
      if (slideTextWrapper) {
        const elements = slideTextWrapper.querySelectorAll('*');
        elements.forEach((el) => {
          el.style.opacity = '0';
          el.style.transform = 'translateY(40px)';
          el.style.animation = 'none';
        });
      }
    });
    
    // Animate elements when slide is shown
    modernBannerCarousel.addEventListener('slid.bs.carousel', function (e) {
      const activeSlide = e.target.querySelector('.carousel-item.active');
      const slideTextWrapper = activeSlide.querySelector('.slide-text-wrapper');
      if (slideTextWrapper) {
        const subtitle = slideTextWrapper.querySelector('.slide-subtitle');
        const title = slideTextWrapper.querySelector('.slide-title, h1, h2, h3, h4, h5, h6');
        const paragraphs = slideTextWrapper.querySelectorAll('p');
        const btn = slideTextWrapper.querySelector('.slide-btn, a[class*="btn"]');
        
        if (subtitle) {
          setTimeout(() => {
            subtitle.style.opacity = '1';
            subtitle.style.transform = 'translateX(0)';
            subtitle.style.animation = 'slideInFromLeft 0.8s ease both';
          }, 300);
        }
        
        if (title) {
          setTimeout(() => {
            title.style.opacity = '1';
            title.style.transform = 'translateX(0)';
            title.style.animation = 'slideInFromLeft 1s ease both';
          }, 500);
        }
        
        paragraphs.forEach((p, index) => {
          setTimeout(() => {
            p.style.opacity = '1';
            p.style.transform = 'translateY(0)';
            p.style.animation = 'fadeInUp 1s ease both';
          }, 700 + (index * 150));
        });
        
        if (btn) {
          setTimeout(() => {
            btn.style.opacity = '1';
            btn.style.transform = 'translateY(0)';
            btn.style.animation = 'fadeInUp 1s ease both';
          }, 900);
        }
      }
    });
    
    // Initial animation on page load
    window.addEventListener('load', function() {
      const firstSlide = modernBannerCarousel.querySelector('.carousel-item.active');
      if (firstSlide) {
        const slideTextWrapper = firstSlide.querySelector('.slide-text-wrapper');
        if (slideTextWrapper) {
          const subtitle = slideTextWrapper.querySelector('.slide-subtitle');
          const title = slideTextWrapper.querySelector('.slide-title, h1, h2, h3, h4, h5, h6');
          const paragraphs = slideTextWrapper.querySelectorAll('p');
          const btn = slideTextWrapper.querySelector('.slide-btn, a[class*="btn"]');
          
          if (subtitle) {
            setTimeout(() => {
              subtitle.style.opacity = '1';
              subtitle.style.transform = 'translateX(0)';
            }, 500);
          }
          
          if (title) {
            setTimeout(() => {
              title.style.opacity = '1';
              title.style.transform = 'translateX(0)';
            }, 700);
          }
          
          paragraphs.forEach((p, index) => {
            setTimeout(() => {
              p.style.opacity = '1';
              p.style.transform = 'translateY(0)';
            }, 900 + (index * 150));
          });
          
          if (btn) {
            setTimeout(() => {
              btn.style.opacity = '1';
              btn.style.transform = 'translateY(0)';
            }, 1100);
          }
        }
      }
    });
  }

  /**
   * Theme Toggle
   */
  const themeToggle = select('#theme-toggle');
  const htmlElement = document.documentElement;
  
  // Get saved theme or default to light
  const savedTheme = localStorage.getItem('theme') || 'light';
  htmlElement.setAttribute('data-theme', savedTheme);
  
  // Theme change handler with background re-initialization
  let themeChangeTimeout = null;
  const handleThemeChange = () => {
    if (themeChangeTimeout) {
      clearTimeout(themeChangeTimeout);
    }
    
    const currentTheme = htmlElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    htmlElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Add animation class
    if (themeToggle) {
      themeToggle.classList.add('theme-switching');
      setTimeout(() => {
        themeToggle.classList.remove('theme-switching');
      }, 300);
    }
    
    // Re-initialize background after theme change (debounced)
    themeChangeTimeout = setTimeout(() => {
      try {
        bgInitialized = false; // Allow re-initialization
        init3DBackground();
      } catch (e) {
        console.error('Error re-initializing background on theme change:', e);
      }
      themeChangeTimeout = null;
    }, 300);
  };
  
  if (themeToggle) {
    themeToggle.addEventListener('click', handleThemeChange);
  }

  /**
   * Auth Modal Handling
   */
  const authModal = select('#authModal');
  const loginForm = select('#loginForm');
  
  if (authModal && loginForm) {
    // Handle form submission via AJAX
    loginForm.addEventListener('submit', function(e) {
      e.preventDefault(); // Предотвращаем стандартную отправку формы
      
      const submitBtn = this.querySelector('.auth-submit-btn');
      const formData = new FormData(this);
      const t = window.TRANSLATIONS || {};
      
      // Удаляем предыдущие сообщения об ошибках
      const existingAlerts = this.querySelectorAll('.alert');
      existingAlerts.forEach(alert => alert.remove());
      
      // Показываем состояние загрузки
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span>${t.processing || 'Processing...'}</span><i class="bi bi-arrow-repeat spin"></i>`;
      }
      
      // Отправляем AJAX запрос
      fetch(this.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin'
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // Успешный вход - закрываем модальное окно и перезагружаем страницу
          if (typeof jQuery !== 'undefined') {
            jQuery(authModal).modal('hide');
          }
          // Перенаправляем на указанную страницу или перезагружаем текущую
          if (data.redirect) {
            window.location.href = data.redirect;
          } else {
            window.location.reload();
          }
        } else {
          // Ошибка входа - показываем сообщение об ошибке
          const errorAlert = document.createElement('div');
          errorAlert.className = 'alert alert-danger alert-dismissible fade show';
          errorAlert.setAttribute('role', 'alert');
          errorAlert.innerHTML = `
            ${data.error || (t.connection_error || 'Login error occurred')}
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
              <span aria-hidden="true">&times;</span>
            </button>
          `;
          
          // Вставляем сообщение об ошибке перед формой
          const formGroup = this.querySelector('.auth-form-group');
          if (formGroup) {
            this.insertBefore(errorAlert, formGroup);
          } else {
            this.insertBefore(errorAlert, this.firstChild);
          }
          
          // Восстанавливаем кнопку
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `<span>${t.login || 'Login'}</span><i class="bi bi-arrow-right"></i>`;
          }
        }
      })
      .catch(error => {
        console.error('Ошибка при отправке формы:', error);
        
        // Показываем общую ошибку
        const errorAlert = document.createElement('div');
        errorAlert.className = 'alert alert-danger alert-dismissible fade show';
        errorAlert.setAttribute('role', 'alert');
        errorAlert.innerHTML = `
          ${t.connection_error || 'Connection error. Please try again.'}
          <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
          </button>
        `;
        
        const formGroup = this.querySelector('.auth-form-group');
        if (formGroup) {
          this.insertBefore(errorAlert, formGroup);
        } else {
          this.insertBefore(errorAlert, this.firstChild);
        }
        
        // Восстанавливаем кнопку
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = `<span>${t.login || 'Login'}</span><i class="bi bi-arrow-right"></i>`;
        }
      });
    });
    
    // Clear form on modal close (Bootstrap 4 with jQuery)
    if (typeof jQuery !== 'undefined') {
      jQuery(authModal).on('hidden.bs.modal', function() {
        if (loginForm) {
          loginForm.reset();
          // Удаляем сообщения об ошибках
          const alerts = loginForm.querySelectorAll('.alert');
          alerts.forEach(alert => alert.remove());
          
          const submitBtn = loginForm.querySelector('.auth-submit-btn');
          const t = window.TRANSLATIONS || {};
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `<span>${t.login || 'Login'}</span><i class="bi bi-arrow-right"></i>`;
          }
        }
      });
    }
  }
  
  // Handle Registration Form
  const registerForm = select('#registerForm');
  const contactTypeRadios = select('input[name="contact_type"]', true);
  const phoneGroup = select('#phone-group');
  const messengerGroup = select('#messenger-group');
  const phoneInput = select('#register-phone');
  const messengerInput = select('#register-messenger');
  
  // Toggle between phone and messenger fields
  if (contactTypeRadios && contactTypeRadios.length > 0) {
    contactTypeRadios.forEach(radio => {
      radio.addEventListener('change', function() {
        if (this.value === 'phone') {
          if (phoneGroup) phoneGroup.style.display = 'block';
          if (messengerGroup) messengerGroup.style.display = 'none';
          if (phoneInput) phoneInput.required = true;
          if (messengerInput) messengerInput.required = false;
          if (messengerInput) messengerInput.value = '';
        } else if (this.value === 'messenger') {
          if (phoneGroup) phoneGroup.style.display = 'none';
          if (messengerGroup) messengerGroup.style.display = 'block';
          if (phoneInput) phoneInput.required = false;
          if (messengerInput) messengerInput.required = true;
          if (phoneInput) phoneInput.value = '';
        }
      });
    });
    
    // Initialize on page load
    const checkedRadio = select('input[name="contact_type"]:checked');
    if (checkedRadio && checkedRadio.value === 'messenger') {
      if (phoneGroup) phoneGroup.style.display = 'none';
      if (messengerGroup) messengerGroup.style.display = 'block';
      if (phoneInput) phoneInput.required = false;
      if (messengerInput) messengerInput.required = true;
    }
  }
  
  if (registerForm) {
    registerForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const submitBtn = this.querySelector('#registerSubmitBtn');
      const errorDiv = select('#registerError');
      const successDiv = select('#registerSuccess');
      const formData = new FormData(this);
      
      // Hide previous messages
      if (errorDiv) errorDiv.style.display = 'none';
      if (successDiv) successDiv.style.display = 'none';
      
      const t = window.TRANSLATIONS || {};
      
      // Validate password match
      const password = formData.get('password');
      const passwordConfirm = formData.get('password_confirm');
      if (password !== passwordConfirm) {
        if (errorDiv) {
          errorDiv.textContent = t.passwords_not_match || 'Passwords do not match';
          errorDiv.style.display = 'block';
        }
        return;
      }
      
      // Validate contact info
      const contactType = formData.get('contact_type');
      const phone = formData.get('phone');
      const messengerLink = formData.get('messenger_link');
      
      if (contactType === 'phone' && !phone) {
        if (errorDiv) {
          errorDiv.textContent = t.phone_required || 'Phone number is required';
          errorDiv.style.display = 'block';
        }
        return;
      }
      
      if (contactType === 'messenger' && !messengerLink) {
        if (errorDiv) {
          errorDiv.textContent = t.messenger_required || 'Messenger link is required';
          errorDiv.style.display = 'block';
        }
        return;
      }
      
      // Show loading state
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span>${t.processing || 'Processing...'}</span><i class="bi bi-arrow-repeat spin"></i>`;
      }
      
      // Send AJAX request
      fetch(this.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          if (successDiv) {
            successDiv.textContent = data.message || 'Регистрация успешна!';
            successDiv.style.display = 'block';
          }
          
          // Redirect after short delay
          setTimeout(() => {
            window.location.href = data.redirect || '/';
          }, 1500);
        } else {
          if (errorDiv) {
            errorDiv.textContent = data.error || 'Ошибка при регистрации';
            errorDiv.style.display = 'block';
          }
          
          const t = window.TRANSLATIONS || {};
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `<span>${t.register || 'Register'}</span><i class="bi bi-person-plus"></i>`;
          }
        }
      })
      .catch(error => {
        console.error('Registration error:', error);
        const t = window.TRANSLATIONS || {};
        if (errorDiv) {
          errorDiv.textContent = t.form_submit_error || 'Error submitting form. Please try again.';
          errorDiv.style.display = 'block';
        }
        
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = `<span>${t.register || 'Register'}</span><i class="bi bi-person-plus"></i>`;
        }
      });
    });
  }
  
  // Add spin animation for loading
  const style = document.createElement('style');
  style.textContent = `
    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    .spin {
      animation: spin 1s linear infinite;
    }
  `;
  document.head.appendChild(style);

  /**
   * 3D Animated Background with Flying Notes
   */
  let bgInitialized = false;
  
  function init3DBackground() {
    // Skip if already initialized
    if (bgInitialized) {
      return;
    }
    
    try {
      // Use direct DOM query instead of select function to ensure it works
      const animatedBg = document.getElementById('animated-3d-bg');
      const notesContainer = document.querySelector('.flying-notes-container');
      
      // Check if containers exist
      if (!animatedBg || !notesContainer) {
        return;
      }
      
      // Check if we're on home page (check data attributes or URL)
      const pageType = animatedBg.getAttribute('data-page-type');
      const pageSlug = animatedBg.getAttribute('data-page-slug');
      const isHomePage = pageType === 'homepage' || pageSlug === 'home' || window.location.pathname === '/' || window.location.pathname === '/home/';
      
      if (!isHomePage) {
        // Hide background if not on home page
        animatedBg.style.display = 'none';
        return;
      }
      
      console.log('3D Background: Initializing on home page...');
      
      // Show background and initialize notes
      animatedBg.style.display = 'block';
      animatedBg.classList.add('show-bg');
      
      // Clear existing notes if any
      notesContainer.innerHTML = '';
      
      // Musical notes symbols
      const notes = ['♪', '♫', '♬', '♩', '♭', '♯', '♮', '𝄞', '𝄢'];
      
      // Create flying notes dynamically (reduced count for performance)
      const noteCount = 15;
      for (let i = 0; i < noteCount; i++) {
        const note = document.createElement('div');
        note.className = 'flying-note';
        const noteSymbol = notes[Math.floor(Math.random() * notes.length)];
        note.setAttribute('data-note', noteSymbol);
        note.textContent = noteSymbol;
        
        // Random positioning
        note.style.left = Math.random() * 100 + '%';
        note.style.animationDelay = Math.random() * 6 + 's';
        note.style.animationDuration = (12 + Math.random() * 18) + 's';
        note.style.fontSize = (30 + Math.random() * 22) + 'px';
        
        // Randomize starting position for 3D depth effect
        const depth = -600 + Math.random() * 1200;
        const startY = 100 + Math.random() * 30;
        note.style.transform = `translateY(${startY}vh) translateZ(${depth}px) rotateX(${Math.random() * 360}deg) rotateY(${Math.random() * 360}deg)`;
        
        notesContainer.appendChild(note);
      }
      
      bgInitialized = true;
      console.log('3D Background: Initialized successfully');
    } catch (error) {
      console.error('Error initializing 3D background:', error);
      bgInitialized = false; // Allow retry on error
    }
  }
  
  // Initialize 3D background after page load
  function initializeBackground() {
    if (!bgInitialized) {
      // Try immediately
      init3DBackground();
      
      // Also try after a delay to ensure DOM is fully ready
      setTimeout(() => {
        if (!bgInitialized) {
          init3DBackground();
        }
      }, 500);
      
      // Final attempt after longer delay
      setTimeout(() => {
        if (!bgInitialized) {
          init3DBackground();
        }
      }, 1500);
    }
  }
  
  // Initialize background when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      setTimeout(initializeBackground, 100);
    });
    window.addEventListener('load', function() {
      setTimeout(initializeBackground, 200);
    });
  } else {
    // DOM already loaded
    setTimeout(initializeBackground, 100);
  }
  
  // Also try after all scripts are loaded
  window.addEventListener('load', function() {
    setTimeout(initializeBackground, 1000);
  });

  /**
   * Shopping Cart Functionality
   */
  class ShoppingCart {
    constructor() {
      this.cart = this.loadCart();
      this.init();
    }

    init() {
      this.updateCartUI();
      this.bindEvents();
    }

    loadCart() {
      try {
        const cartData = localStorage.getItem('shoppingCart');
        return cartData ? JSON.parse(cartData) : [];
      } catch (e) {
        console.error('Error loading cart:', e);
        return [];
      }
    }

    saveCart() {
      try {
        localStorage.setItem('shoppingCart', JSON.stringify(this.cart));
      } catch (e) {
        console.error('Error saving cart:', e);
      }
    }

    addItem(item, quantity = 1) {
      const existingItem = this.cart.find(cartItem => cartItem.id === item.id);
      
      if (existingItem) {
        existingItem.quantity += quantity;
      } else {
        this.cart.push({
          ...item,
          quantity: quantity
        });
      }
      
      this.saveCart();
      this.updateCartUI();
      this.showAddAnimation(item);
    }

    removeItem(itemId) {
      this.cart = this.cart.filter(item => item.id !== itemId);
      this.saveCart();
      this.updateCartUI();
    }

    getTotal() {
      return this.cart.reduce((total, item) => {
        const price = parseFloat(item.price) || 0;
        return total + (price * item.quantity);
      }, 0);
    }

    getItemCount() {
      return this.cart.reduce((count, item) => count + item.quantity, 0);
    }

    updateCartUI() {
      const cartCount = document.getElementById('cartCount');
      const cartItems = document.getElementById('cartItems');
      const cartTotal = document.getElementById('cartTotal');
      const checkoutBtn = document.getElementById('checkoutBtn');

      // Update cart count badge
      const itemCount = this.getItemCount();
      if (cartCount) {
        cartCount.textContent = itemCount;
        if (itemCount > 0) {
          cartCount.classList.add('has-items');
          setTimeout(() => cartCount.classList.remove('has-items'), 500);
        }
      }

      // Update cart items list
      if (cartItems) {
        if (this.cart.length === 0) {
          cartItems.innerHTML = `
            <div class="cart-empty-message">
              <i class="bi bi-cart-x"></i>
              <p>${(window.TRANSLATIONS && window.TRANSLATIONS.cart_empty) || 'Cart is empty'}</p>
            </div>
          `;
        } else {
          cartItems.innerHTML = this.cart.map(item => {
            const itemTotal = (parseFloat(item.price) || 0) * item.quantity;
            const imageHtml = item.image ? `<img src="${item.image}" alt="${item.name}" class="cart-item-thumb">` : '<div class="cart-item-thumb-placeholder"><i class="bi bi-image"></i></div>';
            return `
            <div class="cart-item" data-item-id="${item.id}">
              <div class="cart-item-image-wrapper">
                ${imageHtml}
              </div>
              <div class="cart-item-info">
                <div class="cart-item-name">${item.name}</div>
                <div class="cart-item-details">
                  <span class="cart-item-quantity">${(window.TRANSLATIONS && window.TRANSLATIONS.quantity) || 'Quantity'}: ${item.quantity}</span>
                  <span class="cart-item-price">${item.price} ₾ × ${item.quantity} = ${itemTotal.toFixed(2)} ₾</span>
                </div>
              </div>
              <button class="cart-item-remove" data-item-id="${item.id}" aria-label="${(window.TRANSLATIONS && window.TRANSLATIONS.remove) || 'Remove'}">
                <i class="bi bi-x-circle"></i>
              </button>
            </div>
          `;
          }).join('');

          // Bind remove buttons
          cartItems.querySelectorAll('.cart-item-remove').forEach(btn => {
            btn.addEventListener('click', (e) => {
              const itemId = e.currentTarget.getAttribute('data-item-id');
              this.removeItem(itemId);
            });
          });
        }
      }

      // Update total
      if (cartTotal) {
        cartTotal.textContent = this.getTotal().toFixed(2);
      }

      // Enable/disable checkout button
      if (checkoutBtn) {
        checkoutBtn.disabled = this.cart.length === 0;
      }
    }

    showAddAnimation(item) {
      const button = document.querySelector(`[data-equipment-id="${item.id}"]`);
      if (button) {
        button.classList.add('added');
        setTimeout(() => {
          button.classList.remove('added');
        }, 1000);
      }
    }

    bindEvents() {
      // Order buttons - открывают модальное окно выбора количества
      document.querySelectorAll('.btn-order-equipment').forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.preventDefault();
          const itemData = {
            id: btn.getAttribute('data-equipment-id'),
            name: btn.getAttribute('data-equipment-name'),
            price: btn.getAttribute('data-equipment-price'),
            image: btn.getAttribute('data-equipment-image'),
            maxQuantity: parseInt(btn.getAttribute('data-equipment-quantity')) || 999
          };
          this.openQuantityModal(itemData);
        });
      });

      // Quantity modal controls
      const quantityDecrease = document.getElementById('quantityDecrease');
      const quantityIncrease = document.getElementById('quantityIncrease');
      const quantityInput = document.getElementById('quantityInput');
      const addToCartBtn = document.getElementById('addToCartBtn');

      if (quantityDecrease) {
        quantityDecrease.addEventListener('click', () => {
          const currentValue = parseInt(quantityInput.value) || 1;
          if (currentValue > 1) {
            quantityInput.value = currentValue - 1;
            this.updateQuantityTotal();
          }
        });
      }

      if (quantityIncrease) {
        quantityIncrease.addEventListener('click', () => {
          const currentValue = parseInt(quantityInput.value) || 1;
          const maxValue = parseInt(quantityInput.getAttribute('max')) || 999;
          if (currentValue < maxValue) {
            quantityInput.value = currentValue + 1;
            this.updateQuantityTotal();
          }
        });
      }

      if (addToCartBtn) {
        addToCartBtn.addEventListener('click', () => {
          const quantity = parseInt(quantityInput.value) || 1;
          if (this.currentItem) {
            this.addItem(this.currentItem, quantity);
            if (typeof jQuery !== 'undefined') {
              jQuery('#quantityModal').modal('hide');
            }
            // Показываем корзину после добавления
            setTimeout(() => {
              if (typeof jQuery !== 'undefined') {
                jQuery('#cartModal').modal('show');
              }
            }, 300);
          }
        });
      }

      // Cart button
      const cartButton = document.getElementById('cartButton');
      if (cartButton) {
        cartButton.addEventListener('click', (e) => {
          e.preventDefault();
          if (typeof jQuery !== 'undefined') {
            jQuery('#cartModal').modal('show');
          }
        });
      }

      // Checkout button
      const checkoutBtn = document.getElementById('checkoutBtn');
      if (checkoutBtn) {
        checkoutBtn.addEventListener('click', () => {
          if (this.cart.length > 0) {
            this.openCheckoutModal();
          }
        });
      }

      // Обработчики для правильного закрытия модальных окон и удаления backdrop
      this.setupModalCleanup();
      
      // Checkout form handler
      this.setupCheckoutForm();
    }

    openCheckoutModal() {
      // Закрываем корзину
      if (typeof jQuery !== 'undefined') {
        jQuery('#cartModal').modal('hide');
      }
      
      // Устанавливаем итоговую сумму
      const checkoutTotal = document.getElementById('checkoutTotal');
      if (checkoutTotal) {
        checkoutTotal.textContent = this.getTotal().toFixed(2);
      }
      
      // Очищаем форму
      const form = document.getElementById('checkoutForm');
      if (form) {
        form.reset();
        const errorDiv = document.getElementById('checkoutError');
        if (errorDiv) {
          errorDiv.style.display = 'none';
        }
      }
      
      // Показываем модальное окно оформления заказа
      if (typeof jQuery !== 'undefined') {
        jQuery('#checkoutModal').modal('show');
      }
    }

    setupCheckoutForm() {
      const form = document.getElementById('checkoutForm');
      if (!form) return;
      
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        this.submitOrder();
      });
    }

    async submitOrder() {
      const submitBtn = document.getElementById('submitOrderBtn');
      const errorDiv = document.getElementById('checkoutError');
      
      // Получаем элементы формы
      const customerNameEl = document.getElementById('customerName');
      const customerPhoneEl = document.getElementById('customerPhone');
      const customerEmailEl = document.getElementById('customerEmail');
      const deliveryAddressEl = document.getElementById('deliveryAddress');
      const customerCommentEl = document.getElementById('customerComment');
      const t = window.TRANSLATIONS || {};
      
      // Проверяем, что все элементы существуют
      if (!customerNameEl || !customerPhoneEl || !deliveryAddressEl) {
        console.error('Form elements not found');
        this.showCheckoutError(t.form_elements_not_found || 'Error: form elements not found. Please refresh the page.');
        return;
      }
      
      // Получаем данные формы
      const formData = {
        customer_name: customerNameEl.value.trim(),
        customer_phone: customerPhoneEl.value.trim(),
        customer_email: customerEmailEl ? customerEmailEl.value.trim() : '',
        delivery_address: deliveryAddressEl.value.trim(),
        customer_comment: customerCommentEl ? customerCommentEl.value.trim() : '',
        cart_items: this.cart
      };
      
      // Логируем данные для отладки (без чувствительной информации)
      console.log('Submitting order with', {
        customer_name: formData.customer_name,
        customer_phone: formData.customer_phone ? '***' : '',
        items_count: formData.cart_items.length
      });
      
      // Валидация
      if (!formData.customer_name) {
        this.showCheckoutError(t.please_enter_name || 'Please enter your name');
        return;
      }
      if (!formData.customer_phone) {
        this.showCheckoutError(t.please_enter_phone || 'Please enter your phone number');
        return;
      }
      if (!formData.delivery_address) {
        this.showCheckoutError(t.please_enter_address || 'Please enter delivery address');
        return;
      }
      if (this.cart.length === 0) {
        this.showCheckoutError(t.cart_empty || 'Cart is empty');
        return;
      }
      
      // Блокируем кнопку отправки
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<i class="bi bi-hourglass-split"></i> ${t.processing || 'Processing...'}`;
      }
      
      // Скрываем ошибки
      if (errorDiv) {
        errorDiv.style.display = 'none';
      }
      
      try {
        // Получаем CSRF токен из cookie или из мета-тега
        let csrftoken = this.getCookie('csrftoken');
        
        // Если токен не найден в cookie, пытаемся получить из мета-тега
        if (!csrftoken) {
          const metaToken = document.querySelector('meta[name="csrf-token"]');
          if (metaToken) {
            csrftoken = metaToken.getAttribute('content');
          }
        }
        
        // Если токен все еще не найден, пытаемся получить из скрытого поля формы
        if (!csrftoken) {
          const csrfInput = document.querySelector('[name="csrfmiddlewaretoken"]');
          if (csrfInput) {
            csrftoken = csrfInput.value;
          }
        }
        
        if (!csrftoken) {
          console.error('CSRF token not found');
          this.showCheckoutError(t.security_error || 'Security error. Please refresh the page and try again.');
          return;
        }
        
        // Отправляем запрос
        const response = await fetch('/api/create-order/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
          },
          credentials: 'same-origin',
          body: JSON.stringify(formData)
        });
        
        // Проверяем статус ответа
        if (!response.ok) {
          let errorMessage = `${t.server_error || 'Server error'} ${response.status}`;
          try {
            const errorData = await response.json();
            errorMessage = errorData.error || errorMessage;
          } catch (e) {
            // Если не удалось распарсить JSON, используем текст ответа
            const text = await response.text();
            if (text) {
              errorMessage = text;
            }
          }
          throw new Error(errorMessage);
        }
        
        const data = await response.json();
        
        if (data.success) {
          // Успешное создание заказа
          // Показываем сообщение об успехе в модальном окне
          const successMsg = data.message || (t.order_success ? t.order_success.replace('%(order_number)s', data.order_number) : `Order #${data.order_number} has been successfully created!`);
          this.showCheckoutSuccess(successMsg);
          
          // Очищаем корзину
          this.cart = [];
          this.saveCart();
          this.updateCartUI();
          
          // Очищаем форму
          const form = document.getElementById('checkoutForm');
          if (form) {
            form.reset();
          }
          
          // Закрываем модальные окна через 3 секунды
          setTimeout(() => {
            if (typeof jQuery !== 'undefined') {
              jQuery('#checkoutModal').modal('hide');
              jQuery('#cartModal').modal('hide');
            }
          }, 3000);
        } else {
          // Ошибка создания заказа
          const t = window.TRANSLATIONS || {};
          this.showCheckoutError(data.error || (t.order_creation_error || 'Error creating order'));
        }
      } catch (error) {
        console.error('Error submitting order:', error);
        const t = window.TRANSLATIONS || {};
        const errorMessage = error.message || (t.order_submit_error || 'Error submitting order. Please try again.');
        this.showCheckoutError(errorMessage);
      } finally {
        // Разблокируем кнопку
        const t = window.TRANSLATIONS || {};
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = `<i class="bi bi-check-circle"></i> ${t.confirm_order || 'Confirm Order'}`;
        }
      }
    }

    showCheckoutError(message) {
      const errorDiv = document.getElementById('checkoutError');
      const successDiv = document.getElementById('checkoutSuccess');
      if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        errorDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
      // Скрываем сообщение об успехе, если оно было показано
      if (successDiv) {
        successDiv.style.display = 'none';
      }
    }

    showCheckoutSuccess(message) {
      const successDiv = document.getElementById('checkoutSuccess');
      const errorDiv = document.getElementById('checkoutError');
      if (successDiv) {
        successDiv.innerHTML = `<i class="bi bi-check-circle"></i> ${message}`;
        successDiv.style.display = 'block';
        successDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
      // Скрываем ошибки, если они были показаны
      if (errorDiv) {
        errorDiv.style.display = 'none';
      }
    }

    getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }

    setupModalCleanup() {
      // Функция для очистки backdrop и стилей
      const cleanupBackdrop = () => {
        // Удаляем все backdrop элементы
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => backdrop.remove());
        
        // Убираем класс modal-open с body
        document.body.classList.remove('modal-open');
        
        // Убираем inline стили padding-right если они остались
        document.body.style.paddingRight = '';
        
        // Убираем overflow: hidden если он был установлен
        document.body.style.overflow = '';
      };

      // Обработка закрытия модального окна корзины
      const cartModal = document.getElementById('cartModal');
      if (cartModal) {
        cartModal.addEventListener('hidden.bs.modal', cleanupBackdrop);
        cartModal.addEventListener('hide.bs.modal', function() {
          // Предотвращаем множественные backdrop
          cleanupBackdrop();
        });
      }

      // Обработка закрытия модального окна выбора количества
      const quantityModal = document.getElementById('quantityModal');
      if (quantityModal) {
        quantityModal.addEventListener('hidden.bs.modal', cleanupBackdrop);
        quantityModal.addEventListener('hide.bs.modal', function() {
          // Предотвращаем множественные backdrop
          cleanupBackdrop();
        });
      }

      // Обработка закрытия модального окна просмотра фото
      const equipmentPhotoModal = document.getElementById('equipmentPhotoModal');
      if (equipmentPhotoModal) {
        equipmentPhotoModal.addEventListener('hidden.bs.modal', cleanupBackdrop);
        equipmentPhotoModal.addEventListener('hide.bs.modal', function() {
          cleanupBackdrop();
        });
      }
      
      // Обработка закрытия модального окна оформления заказа
      const checkoutModal = document.getElementById('checkoutModal');
      if (checkoutModal) {
        checkoutModal.addEventListener('hidden.bs.modal', cleanupBackdrop);
        checkoutModal.addEventListener('hide.bs.modal', function() {
          cleanupBackdrop();
        });
      }

      // Обработка клика по кнопке "Продолжить покупки"
      const continueShoppingBtn = document.getElementById('continueShoppingBtn');
      if (continueShoppingBtn) {
        continueShoppingBtn.addEventListener('click', function(e) {
          e.preventDefault();
          e.stopPropagation();
          
          // Закрываем модальное окно
          if (typeof jQuery !== 'undefined' && typeof jQuery.fn.modal !== 'undefined') {
            jQuery('#cartModal').modal('hide');
          } else if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const modalElement = document.getElementById('cartModal');
            if (modalElement) {
              const modalInstance = bootstrap.Modal.getInstance(modalElement);
              if (modalInstance) {
                modalInstance.hide();
              } else {
                const modal = new bootstrap.Modal(modalElement);
                modal.hide();
              }
            }
          } else {
            // Простое закрытие через CSS
            const modal = document.getElementById('cartModal');
            if (modal) {
              modal.classList.remove('show');
              modal.style.display = 'none';
              cleanupBackdrop();
            }
          }
          
          // Очистка после небольшой задержки
          setTimeout(cleanupBackdrop, 300);
        });
      }

      // Обработка клика по кнопке закрытия (крестик) для всех модальных окон
      document.querySelectorAll('.modal .close[data-dismiss="modal"]').forEach(closeBtn => {
        closeBtn.addEventListener('click', function(e) {
          e.preventDefault();
          e.stopPropagation();
          const modal = this.closest('.modal');
          if (modal) {
            if (typeof jQuery !== 'undefined' && typeof jQuery.fn.modal !== 'undefined') {
              jQuery(modal).modal('hide');
            } else if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
              const modalInstance = bootstrap.Modal.getInstance(modal);
              if (modalInstance) {
                modalInstance.hide();
              }
            } else {
              // Простое закрытие через CSS
              modal.classList.remove('show');
              modal.style.display = 'none';
              cleanupBackdrop();
            }
            // Очистка после небольшой задержки
            setTimeout(cleanupBackdrop, 300);
          }
        });
      });

      // Обработка клика вне модального окна (на backdrop)
      document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
          if (e.target === this) {
            if (typeof jQuery !== 'undefined') {
              jQuery(this).modal('hide');
            } else {
              const modalInstance = bootstrap.Modal.getInstance(this);
              if (modalInstance) {
                modalInstance.hide();
              }
            }
            setTimeout(cleanupBackdrop, 300);
          }
        });
      });
    }

    openQuantityModal(itemData) {
      this.currentItem = itemData;
      
      // Заполняем данные в модальном окне
      const itemImage = document.getElementById('quantityItemImage');
      const itemName = document.getElementById('quantityItemName');
      const itemPrice = document.getElementById('quantityItemPrice');
      const quantityInput = document.getElementById('quantityInput');
      const quantityError = document.getElementById('quantityError');

      if (itemImage) {
        itemImage.src = itemData.image || '';
        itemImage.alt = itemData.name || '';
      }
      if (itemName) {
        itemName.textContent = itemData.name || '';
      }
      if (itemPrice) {
        itemPrice.textContent = `${itemData.price} ₾`;
      }
      if (quantityInput) {
        quantityInput.value = 1;
        quantityInput.setAttribute('max', itemData.maxQuantity || 999);
      }
      if (quantityError) {
        quantityError.style.display = 'none';
      }

      this.updateQuantityTotal();

      // Показываем модальное окно
      if (typeof jQuery !== 'undefined') {
        jQuery('#quantityModal').modal('show');
      }
    }

    updateQuantityTotal() {
      const quantityInput = document.getElementById('quantityInput');
      const quantityTotal = document.getElementById('quantityTotal');
      const quantityError = document.getElementById('quantityError');
      const addToCartBtn = document.getElementById('addToCartBtn');

      if (!this.currentItem || !quantityInput || !quantityTotal) return;

      const quantity = parseInt(quantityInput.value) || 1;
      const price = parseFloat(this.currentItem.price) || 0;
      const maxQuantity = parseInt(quantityInput.getAttribute('max')) || 999;
      const total = price * quantity;

      quantityTotal.textContent = total.toFixed(2);

      // Проверка доступности
      const t = window.TRANSLATIONS || {};
      if (quantity > maxQuantity) {
        if (quantityError) {
          const availableMsg = t.only_available || 'Only %(quantity)s available';
          quantityError.textContent = availableMsg.replace('%(quantity)s', maxQuantity);
          quantityError.style.display = 'block';
        }
        if (addToCartBtn) {
          addToCartBtn.disabled = true;
        }
      } else {
        if (quantityError) {
          quantityError.style.display = 'none';
        }
        if (addToCartBtn) {
          addToCartBtn.disabled = false;
        }
      }
    }
  }

  /**
   * Equipment Photo Gallery Functionality
   */
  class EquipmentPhotoGallery {
    constructor() {
      this.init();
    }

    init() {
      this.bindThumbnailHovers();
      this.bindPhotoTriggers();
      this.bindModalThumbnails();
    }

    bindThumbnailHovers() {
      // Функция для применения стилей к контейнеру и миниатюрам
      const applyThumbnailStyles = () => {
        document.querySelectorAll('.equipment-thumbnails').forEach(thumbnailsContainer => {
          // Применяем стили напрямую для гарантии
          thumbnailsContainer.style.cssText += 'display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; overflow-x: auto !important; overflow-y: hidden !important; align-items: flex-start !important; justify-content: flex-start !important; width: 100% !important; max-width: 100% !important; margin: 0 !important; padding: 5px 0 !important; gap: 10px !important;';
          
          // Убеждаемся, что все миниатюры имеют правильные стили
          thumbnailsContainer.querySelectorAll('.equipment-thumb').forEach((thumb, index) => {
            thumb.style.cssText += 'display: block !important; flex-shrink: 0 !important; flex-grow: 0 !important; flex-basis: 80px !important; width: 80px !important; height: 80px !important; min-width: 80px !important; max-width: 80px !important; margin: 0 !important; float: none !important; clear: none !important;';
            
            // Удаляем старые обработчики, если они есть (через data-атрибут)
            if (!thumb.hasAttribute('data-thumb-bound')) {
              thumb.setAttribute('data-thumb-bound', 'true');
              
              // Добавляем обработчик события
              thumb.addEventListener('mouseenter', (e) => {
                const imageUrl = e.currentTarget.getAttribute('data-image-url');
                const gallery = e.currentTarget.closest('.equipment-photo-gallery');
                if (gallery && imageUrl) {
                  const mainPhoto = gallery.querySelector('.main-equipment-photo');
                  const trigger = gallery.querySelector('.equipment-photo-trigger');
                  if (mainPhoto) {
                    mainPhoto.src = imageUrl;
                  }
                  if (trigger) {
                    trigger.setAttribute('data-main-image', imageUrl);
                  }
                  // Обновляем активный класс
                  const thumbnailsContainer = e.currentTarget.closest('.equipment-thumbnails');
                  if (thumbnailsContainer) {
                    thumbnailsContainer.querySelectorAll('.equipment-thumb').forEach(t => t.classList.remove('active'));
                    e.currentTarget.classList.add('active');
                  }
                }
              });
            }
          });
        });
      };
      
      // Применяем стили сразу
      applyThumbnailStyles();
      
      // Применяем стили после загрузки DOM
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', applyThumbnailStyles);
      }
      
      // Применяем стили после полной загрузки страницы
      window.addEventListener('load', applyThumbnailStyles);
      
      // Применяем стили при изменении размера окна
      let resizeTimeout;
      window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(applyThumbnailStyles, 100);
      });
      
      // Используем MutationObserver для отслеживания изменений DOM
      const observer = new MutationObserver((mutations) => {
        let shouldApply = false;
        mutations.forEach((mutation) => {
          if (mutation.addedNodes.length > 0) {
            mutation.addedNodes.forEach((node) => {
              if (node.nodeType === 1 && (node.classList.contains('equipment-thumbnails') || node.querySelector('.equipment-thumbnails'))) {
                shouldApply = true;
              }
            });
          }
        });
        if (shouldApply) {
          setTimeout(applyThumbnailStyles, 50);
        }
      });
      
      observer.observe(document.body, {
        childList: true,
        subtree: true
      });
    }

    bindPhotoTriggers() {
      // Открытие модального окна при клике на фото
      document.querySelectorAll('.equipment-photo-trigger').forEach(trigger => {
        trigger.addEventListener('click', (e) => {
          e.preventDefault();
          const mainImageUrl = trigger.getAttribute('data-main-image');
          const equipmentName = trigger.getAttribute('data-equipment-name');
          const gallery = trigger.closest('.equipment-photo-gallery');
          const thumbnails = gallery ? gallery.querySelectorAll('.equipment-thumb') : [];
          
          // Устанавливаем основное фото
          const mainPhoto = document.getElementById('equipmentPhotoMain');
          const photoTitle = document.getElementById('equipmentPhotoTitle');
          const thumbnailsContainer = document.getElementById('equipmentPhotoThumbnails');
          
          if (mainPhoto && mainImageUrl) {
            // Используем оригинальное изображение (убеждаемся, что это полный URL)
            const fullImageUrl = mainImageUrl.startsWith('http') ? mainImageUrl : window.location.origin + mainImageUrl;
            
            // Устанавливаем стили для правильного отображения
            mainPhoto.style.maxWidth = '100%';
            mainPhoto.style.width = 'auto';
            mainPhoto.style.maxHeight = '70vh';
            mainPhoto.style.height = 'auto';
            mainPhoto.style.objectFit = 'contain';
            mainPhoto.style.display = 'block';
            mainPhoto.style.margin = '0 auto';
            
            mainPhoto.style.opacity = '0';
            mainPhoto.style.transition = 'opacity 0.3s ease';
            mainPhoto.src = fullImageUrl;
            mainPhoto.alt = equipmentName || 'Фото товара';
            
            mainPhoto.onload = function() {
              this.style.opacity = '1';
              console.log('Изображение загружено:', fullImageUrl);
            };
            mainPhoto.onerror = function() {
              console.error('Ошибка загрузки изображения:', fullImageUrl);
              this.style.opacity = '1';
              // Пробуем оригинальный URL
              this.src = mainImageUrl;
            };
          }
          if (photoTitle && equipmentName) {
            photoTitle.textContent = equipmentName;
          }
          
          // Добавляем миниатюры в модальное окно
          if (thumbnailsContainer) {
            thumbnailsContainer.innerHTML = '';
            // Убеждаемся, что контейнер имеет правильные стили с !important
            thumbnailsContainer.style.cssText += 'display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; overflow-x: auto !important; overflow-y: hidden !important; align-items: flex-start !important; justify-content: flex-start !important; width: 100% !important; max-width: 100% !important; margin: 0 !important; padding: 15px !important; gap: 12px !important;';
            
            thumbnails.forEach((thumb, index) => {
              const imageUrl = thumb.getAttribute('data-image-url');
              const thumbImg = thumb.querySelector('img');
              if (imageUrl && thumbImg) {
                const thumbWrapper = document.createElement('div');
                thumbWrapper.className = 'equipment-thumb-modal';
                // Применяем стили напрямую для гарантии с !important
                thumbWrapper.style.cssText += 'display: block !important; flex-shrink: 0 !important; flex-grow: 0 !important; flex-basis: 90px !important; width: 90px !important; height: 90px !important; min-width: 90px !important; max-width: 90px !important; margin: 0 !important; float: none !important; clear: none !important;';
                
                if (index === 0 || thumb.classList.contains('active')) {
                  thumbWrapper.classList.add('active');
                }
                thumbWrapper.setAttribute('data-image-url', imageUrl);
                // Используем оригинальное изображение для миниатюры в модальном окне
                thumbWrapper.innerHTML = `<img src="${imageUrl}" alt="Thumbnail ${index + 1}" class="img-fluid" style="width: 100%; height: 100%; object-fit: cover;">`;
                thumbnailsContainer.appendChild(thumbWrapper);
              }
            });
          }
          
          // Показываем модальное окно
          if (typeof jQuery !== 'undefined') {
            jQuery('#equipmentPhotoModal').modal('show');
          }
        });
      });
    }

    bindModalThumbnails() {
      // Используем делегирование событий для динамически созданных элементов
      const modal = document.getElementById('equipmentPhotoModal');
      if (!modal) return;
      
      // Функция для переключения фото
      const switchPhoto = (imageUrl, thumb) => {
        const mainPhotoImg = document.getElementById('equipmentPhotoMain');
        if (mainPhotoImg && imageUrl) {
          // Убеждаемся, что это полный URL оригинального изображения
          const fullImageUrl = imageUrl.startsWith('http') ? imageUrl : window.location.origin + imageUrl;
          
          // Плавное переключение с fade эффектом
          mainPhotoImg.style.opacity = '0';
          mainPhotoImg.style.transition = 'opacity 0.3s ease';
          
          setTimeout(() => {
            mainPhotoImg.src = fullImageUrl;
            mainPhotoImg.onload = function() {
              this.style.opacity = '1';
              console.log('Фото переключено на:', fullImageUrl);
            };
            mainPhotoImg.onerror = function() {
              console.error('Ошибка загрузки изображения:', fullImageUrl);
              this.style.opacity = '1';
              // Пробуем оригинальный URL
              this.src = imageUrl;
            };
          }, 150);
          
          // Обновляем активный класс
          modal.querySelectorAll('.equipment-thumb-modal').forEach(t => t.classList.remove('active'));
          if (thumb) {
            thumb.classList.add('active');
          }
        }
      };
      
      // Обработка наведения на миниатюры в модальном окне
      modal.addEventListener('mouseenter', (e) => {
        const thumb = e.target.closest('.equipment-thumb-modal');
        if (thumb) {
          const imageUrl = thumb.getAttribute('data-image-url');
          switchPhoto(imageUrl, thumb);
        }
      }, true);
      
      // Обработка кликов на миниатюры в модальном окне
      modal.addEventListener('click', (e) => {
        const thumb = e.target.closest('.equipment-thumb-modal');
        if (thumb) {
          e.preventDefault();
          const imageUrl = thumb.getAttribute('data-image-url');
          switchPhoto(imageUrl, thumb);
        }
      });
    }
  }

  // Initialize shopping cart
  window.addEventListener('DOMContentLoaded', () => {
    window.shoppingCart = new ShoppingCart();
    window.equipmentPhotoGallery = new EquipmentPhotoGallery();
    
    // Функция для очистки backdrop
    const cleanupBackdrop = () => {
      const backdrops = document.querySelectorAll('.modal-backdrop');
      backdrops.forEach(backdrop => backdrop.remove());
      document.body.classList.remove('modal-open');
      document.body.style.paddingRight = '';
      document.body.style.overflow = '';
    };
    
    // Дополнительная очистка backdrop при загрузке страницы
    cleanupBackdrop();
    
    // Обработка ESC для закрытия модальных окон
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' || e.keyCode === 27) {
        const openModals = document.querySelectorAll('.modal.show');
        openModals.forEach(modal => {
          if (typeof jQuery !== 'undefined') {
            jQuery(modal).modal('hide');
          } else {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
              modalInstance.hide();
            }
          }
        });
        setTimeout(cleanupBackdrop, 300);
      }
    });
    
    // Периодическая проверка и очистка backdrop (на случай если что-то пошло не так)
    setInterval(() => {
      const openModals = document.querySelectorAll('.modal.show');
      if (openModals.length === 0) {
        cleanupBackdrop();
      }
    }, 1000);
  });

  // Очистка backdrop при уходе со страницы
  window.addEventListener('beforeunload', function() {
    const backdrops = document.querySelectorAll('.modal-backdrop');
    backdrops.forEach(backdrop => backdrop.remove());
    document.body.classList.remove('modal-open');
    document.body.style.paddingRight = '';
    document.body.style.overflow = '';
  });

})()