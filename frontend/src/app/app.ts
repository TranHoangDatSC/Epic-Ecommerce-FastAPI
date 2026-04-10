import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterOutlet, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { HeaderComponent } from './layout/components/header/header';
import { FooterComponent } from './layout/components/footer/footer';
import { UIService, ModalConfig } from './core/services/ui.service';

declare var bootstrap: any;

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

  constructor(private router: Router, private uiService: UIService) {
    this.router.events.pipe(filter((event): event is NavigationEnd => event instanceof NavigationEnd)).subscribe((event) => {
      // Hide header/footer for moderator and admin routes
      const isSpecialRoute = event.urlAfterRedirects.startsWith('/moderator') || 
                            event.urlAfterRedirects.startsWith('/admin') ||
                            event.urlAfterRedirects.startsWith('/sellerhub')
      this.showShell.set(!isSpecialRoute);
    });

    this.uiService.modal$.subscribe(config => {
      this.modalConfig = config;
      const modalElement = document.getElementById('globalNotificationModal');
      if (modalElement) {
        const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
        modal.show();
      }
    });
  }
}