import styled from "@emotion/styled";
import { Env } from "@jupiter/webapi-client";

interface EnvBannerProps {
  env: Env;
}

export function EnvBanner({ env }: EnvBannerProps) {
  switch (env) {
    case Env.PRODUCTION:
      return null;
    case Env.STAGING:
      return (
        <EnvBannerSection>
          <div>You are running a staging build</div>
        </EnvBannerSection>
      );
    case Env.LOCAL:
      return (
        <EnvBannerSection>
          <div>You are running a local build</div>
        </EnvBannerSection>
      );
  }
}

const EnvBannerSection = styled("section")`
  z-index: 99999;
  position: fixed;
  bottom: 0vh;
  width: 100%;
  padding-top: 0.25rem;
  padding-bottom: 0.25rem;
  padding-left: 1rem;
  padding-right: 1rem;
  background-color: #ffe08a;
`;
