import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterOutlet, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { HeaderComponent } from './layout/components/header/header';
import { FooterComponent } from './layout/components/footer/footer';

@Component({
  selector: 'app-root',
  imports: [CommonModule, RouterOutlet, HeaderComponent, FooterComponent],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly title = signal('Oldshop Ecommerce');
  protected showShell = signal(true);

  constructor(private router: Router) {
    this.router.events.pipe(filter((event): event is NavigationEnd => event instanceof NavigationEnd)).subscribe((event) => {
      // Hide header/footer for moderator routes
      this.showShell.set(!event.urlAfterRedirects.startsWith('/moderator'));
    });
  }
}
