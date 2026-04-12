import { Component, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterOutlet, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { HeaderComponent } from './layout/components/header/header';
import { FooterComponent } from './layout/components/footer/footer';
import { UIService, ModalConfig } from './core/services/ui.service';

declare var bootstrap: any;

import { AuthService } from './core/services/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, HeaderComponent, FooterComponent],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})

export class App {
  protected readonly title = signal('Oldshop Ecommerce');
  protected showShell = signal(true);
  modalConfig: ModalConfig | null = null;
  authService = inject(AuthService);

  constructor(private router: Router, private uiService: UIService) {
    // Initial check for showShell
    const initialUrl = window.location.pathname;
    const isSpecialRoute = initialUrl.startsWith('/moderator') || initialUrl.startsWith('/admin');
    this.showShell.set(!isSpecialRoute);

    this.router.events.pipe(filter((event): event is NavigationEnd => event instanceof NavigationEnd)).subscribe((event) => {
      // Hide header/footer for moderator and admin routes
      const isSpecialRoute = event.urlAfterRedirects.startsWith('/moderator') || 
                            event.urlAfterRedirects.startsWith('/admin');
      this.showShell.set(!isSpecialRoute);
    });

    this.uiService.modal$.subscribe(config => {
      this.modalConfig = config;
    });

  }
}
