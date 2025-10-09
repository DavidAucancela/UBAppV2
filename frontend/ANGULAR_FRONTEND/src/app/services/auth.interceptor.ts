import { HttpInterceptorFn } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  if (typeof window === 'undefined') {
    return next(req);
  }

  const token = localStorage.getItem('authToken');
  if (!token) {
    return next(req);
  }

  const authReq = req.clone({
    setHeaders: {
      Authorization: `Token ${token}`
    }
  });

  return next(authReq);
};



