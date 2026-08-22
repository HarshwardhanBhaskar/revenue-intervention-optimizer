import React from 'react';
import '../styles/globals.css';
import Layout from '../components/Layout';

export const metadata = {
  title: 'Revenue Intervention Optimizer | Razorpay AI Buildathon',
  description: 'AI-powered incremental revenue recovery optimizing intervention net value.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Layout>{children}</Layout>
      </body>
    </html>
  );
}
