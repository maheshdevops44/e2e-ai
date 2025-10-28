// COMMENTED OUT FOR NOW - WILL NEED LATER
// import type { NextAuthOptions } from 'next-auth';

// const authConfig: NextAuthOptions = {
//   pages: {
//     signIn: '/login',
//     error: '/login',
//   },
//   providers: [],
//   callbacks: {
//     async session({ session, token }) {
//       if (token.id) {
//         session.user.id = token.id as string;
//       }
//       return session;
//     },
//     async jwt({ token, user }) {
//       if (user) {
//         token.id = user.id;
//       }
//       return token;
//     },
//   },
// };

// export default authConfig;

// Minimal export for development - no authentication
const authConfig = null;
export default authConfig;