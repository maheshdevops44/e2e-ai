// COMMENTED OUT FOR NOW - WILL NEED LATER
// import { withAuth } from 'next-auth/middleware';

// export default withAuth(
//   function middleware(req) {
//     // Add any additional middleware logic here
//   },
//   {
//     callbacks: {
//       authorized: ({ token, req }) => {
//         const { pathname } = req.nextUrl;
//         
//         // Allow public routes
//         if (pathname.startsWith('/login') || pathname.startsWith('/register') || pathname.startsWith('/api/auth')) {
//           return true;
//         }
//         
//         // Protect dashboard and workflow routes
//         if (pathname.startsWith('/dashboard') || pathname.startsWith('/workflow')) {
//           return !!token;
//         }
//         
//         // Allow other routes
//         return true;
//       },
//     },
//   }
// );

// Allow all routes for now
export default function middleware(req: any) {
  // No authentication required for now
  return;
}

export const config = {
  matcher: [
    '/dashboard/:path*',
    '/create-test/workflow/:path*',
    '/((?!api/auth|_next/static|_next/image|favicon.ico).*)',
  ],
};