import { Html, Head, Main, NextScript } from "next/document";

export default function Document() {
  return (
    <Html lang="en" className="dark">
      <Head>
        <meta
          name="description"
          content="MLOps Platform - Vercel for ML models"
        />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <body className="bg-background text-foreground">
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
