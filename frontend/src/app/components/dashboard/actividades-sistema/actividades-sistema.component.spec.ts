import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ActividadesSistemaComponent } from './actividades-sistema.component';

describe('ActividadesSistemaComponent', () => {
  let component: ActividadesSistemaComponent;
  let fixture: ComponentFixture<ActividadesSistemaComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ActividadesSistemaComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ActividadesSistemaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
