import React, { createContext, useContext, useEffect, useState } from "react";
import { useMagic } from "../components/auth/magic/MagicContext";
import Loading from "../components/ui/Loading";
import { useDynamicWallet } from "../components/auth/dynamic/dynamicHooks";

type Props = {
  children: React.ReactNode;
};
export type AuthContextType = {
  token: string | null;
  setToken: (token: string) => void;
  address: string | null;
  setAddress: (address: string) => void;

  currentAuthSupply: string;
};
export const AuthContext = createContext<AuthContextType>({
  token: null,
  setToken: () => {},
  address: null,
  setAddress: () => {},
  currentAuthSupply: "",
});

// eslint-disable-next-line react-refresh/only-export-components,
export const useAuth = () => useContext(AuthContext);

const AuthProvider = ({ children }: Props) => {
  const [currentAuthSupply, setCurrentSupply] = useState<"magic" | "dynamic">(
    "magic"
  );

  const [token, setToken] = useState<string | null>(null);
  const [address, setAddress] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const { magic } = useMagic();
  const { address: dynamicAddress, isConnecting: isConnectingDynamic } =
    useDynamicWallet();

  useEffect(() => {
    if (currentAuthSupply === "magic") {
      const fetchData = async () => {
        if (!magic) return console.error("Magic not initialized");
        try {
          console.log("Fetching user metadata");

          setLoading(true);
          const m = await magic.user.getMetadata();
          setAddress(m.publicAddress!);
          // setToken(localStorage.getItem("jwtToken")!);

          setLoading(false);
        } catch (error) {
          console.error(error);
        } finally {
          setLoading(false);
        }
      };
      fetchData();
    }
  }, [currentAuthSupply, magic, setAddress, setToken]);

  useEffect(() => {
    if (currentAuthSupply === "dynamic") {
      setLoading(true);
      if (dynamicAddress) {
        setAddress(dynamicAddress);
      }

      if (!isConnectingDynamic) {
        setLoading(false);
      }
    }
  }, [currentAuthSupply, dynamicAddress, isConnectingDynamic, setAddress]);

  if (loading) {
    return <Loading loading={true} />;
  }

  return (
    <AuthContext.Provider
      value={{ token, setToken, setAddress, address, currentAuthSupply }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;
