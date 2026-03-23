import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-not-found',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './not-found.component.html',
  styleUrls: ['./not-found.component.css']
})
export class NotFoundComponent {
  currentUrl: string = window.location.pathname;

  constructor(private router: Router) {}

  goHome(): void {
    this.router.navigate(['/informacion']);
  }

  goLogin(): void {
    this.router.navigate(['/login']);
  }

  goBack(): void {
    window.history.back();
  }
}
