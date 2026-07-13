import { useTranslation } from "react-i18next";

export function useT() {
  const { t, i18n } = useTranslation();

  const changeLanguage = (lang: string) => {
    i18n.changeLanguage(lang);
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
  };

  const currentLanguage = i18n.language?.startsWith("ar") ? "ar" : "en";

  return { t, i18n, changeLanguage, currentLanguage };
}
