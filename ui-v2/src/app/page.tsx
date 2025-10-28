// import { redirect } from 'next/navigation';
import { redirect } from 'next/navigation';

export default function HomePage() {
  // redirect('/login'); // Commented out for now - will need later
  // Redirect to dashboard instead of login
  redirect('/dashboard');
}
