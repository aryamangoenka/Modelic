import "@/styles/globals.css";
import type { AppProps } from "next/app";
import Head from "next/head";
import { Inter } from "next/font/google";
import { Layout } from "@/components/layout/layout";

const inter = Inter({ subsets: ["latin"] });

export default function App({ Component, pageProps }: AppProps) {
  return (
    <>
      <Head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <div className={inter.className}>
        <Layout>
          <Component {...pageProps} />
        </Layout>
      </div>
    </>
  );
}
