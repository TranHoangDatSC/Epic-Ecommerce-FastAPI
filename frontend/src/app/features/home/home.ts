import { Component, signal, OnInit, OnDestroy } from '@angular/core';
import { RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';

/**
 * Home Component - Professional E-commerce Landing Page
 * Manages product carousel, authentication state, and customer interactions
 */
@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './home.html',
  styleUrl: './home.scss'
})
export class HomeComponent implements OnInit, OnDestroy {
  // ===== AUTHENTICATION STATE =====
  /** User authentication state */
  isLoggedIn = signal(false);

  /** Current logged-in user's full name */
  currentUser = signal<string>('');

  // ===== CAROUSEL STATE =====
  /** Current slide index for product carousel */
  currentSlide = signal(0);

  /** Support agent online status */
  isAgentOnline = signal(true);

  /** Product showcase carousel data */
  carouselImages = [
    { src: '/images/carousel-1.png', alt: 'Sản phẩm mỹ phẩm chính hãng' },
    { src: '/images/carousel-2.png', alt: 'Sản phẩm điện tử đã qua sử dụng' }
  ];

  /** Auto-slide interval reference */
  private slideInterval?: number;

  // ===== LIFECYCLE HOOKS =====
  /**
   * Initialize component - Set up carousel and load user data
   */
  ngOnInit() {
    this.startAutoSlide();
    this.loadUserData();
  }

  /**
   * Cleanup - Stop auto-slide interval
   */
  ngOnDestroy() {
    this.stopAutoSlide();
  }

  // ===== CAROUSEL CONTROL METHODS =====
  /**
   * Start automatic carousel sliding every 5 seconds
   * Respects user pause when manually navigating
   */
  private startAutoSlide() {
    this.slideInterval = window.setInterval(() => {
      this.nextSlide();
    }, 5000);
  }

  /**
   * Stop the auto-slide interval
   */
  private stopAutoSlide() {
    if (this.slideInterval) {
      clearInterval(this.slideInterval);
    }
  }

  /**
   * Navigate to next slide in carousel
   */
  nextSlide() {
    this.currentSlide.update(current =>
      (current + 1) % this.carouselImages.length
    );
  }

  /**
   * Navigate to previous slide in carousel
   */
  prevSlide() {
    this.currentSlide.update(current =>
      current === 0 ? this.carouselImages.length - 1 : current - 1
    );
  }

  /**
   * Jump directly to a specific slide
   * @param index Slide index (0-based)
   */
  goToSlide(index: number) {
    if (index >= 0 && index < this.carouselImages.length) {
      this.currentSlide.set(index);
    }
  }

  // ===== AUTHENTICATION METHODS =====
  /**
   * Load user data from localStorage/AuthService
   * Sets isLoggedIn and currentUser signals
   */
  private loadUserData() {
    try {
      const userData = localStorage.getItem('user');
      if (userData) {
        const user = JSON.parse(userData);
        this.isLoggedIn.set(true);
        this.currentUser.set(user.fullName || user.username || 'Người dùng');
      } else {
        this.isLoggedIn.set(false);
        this.currentUser.set('');
      }
    } catch (error) {
      console.error('Error loading user data:', error);
      this.isLoggedIn.set(false);
      this.currentUser.set('');
    }
  }
}
