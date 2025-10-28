// COMMENTED OUT FOR NOW - WILL NEED LATER
// import { compare } from 'bcrypt-ts';
// import NextAuth, { type DefaultSession } from 'next-auth';
// import Credentials from 'next-auth/providers/credentials';
// import { PrismaAdapter } from '@auth/prisma-adapter';
// import { prisma } from '../prisma';
// import type { NextAuthOptions } from 'next-auth';

// declare module 'next-auth' {
//   interface Session extends DefaultSession {
//     user: {
//       id: string;
//     } & DefaultSession['user'];
//   }
// }

// const authOptions: NextAuthOptions = {
//   pages: {
//     signIn: '/login',
//     error: '/login',
//   },
//   adapter: PrismaAdapter(prisma),
//   providers: [
//     Credentials({
//       name: 'credentials',
//       credentials: {
//         email: { label: 'Email', type: 'email' },
//         password: { label: 'Password', type: 'password' },
//       },
//       async authorize(credentials) {
//         if (!credentials?.email || !credentials?.password) {
//           return null;
//         }

//         const user = await prisma.user.findUnique({
//           where: { email: credentials.email as string },
//         });

//         if (!user) {
//           return null;
//         }

//         const isValid = await compare(credentials.password as string, user.password);

//         if (!isValid) {
//           return null;
//         }

//         return {
//           id: user.id,
//           email: user.email,
//           name: user.name,
//         };
//       },
//     }),
//   ],
//   session: { strategy: 'jwt' },
//   callbacks: {
//     async jwt({ token, user }) {
//       if (user) {
//         token.id = user.id;
//       }
//       return token;
//     },
//     async session({ session, token }) {
//       if (token.id) {
//         session.user.id = token.id as string;
//       }
//       return session;
//     },
//   },
// };

// export { authOptions };
// export default NextAuth(authOptions);

// Minimal export for development - no authentication
export const authOptions = null;
const auth = null;
export default auth;