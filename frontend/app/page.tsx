import AnimalCardSection from "@/components/AnimalCardSection";
import CardSection from "@/components/CardSection";
import CategoryCardSection from "@/components/CategoryCardSection";
import TallCardSection from "@/components/RegionCardSection";
import TopTenSection from "@/components/TopTenSection";
import { createClient } from "@/supabase/server";

const Home = async () => {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000";

  const supabase = await createClient();

  const {
    data: { user },
  } = await supabase.auth.getUser();

  return (
    <>
      <div className="py-10 px-14 flex-1 w-full h-full  flex justify-center">
        <div className="w-full flex flex-col gap-8 min-h-full">
          {user && (
            <CardSection
              title="Recommendations for you"
              apiUrl={`${apiUrl}/dive-sites/recommendations/users/${user.id}`}
            />
          )}
          {user && (
            <TallCardSection
              title="Recommended Regions"
              apiUrl={`${apiUrl}/recommendations/recommend_dive_regions/${user.id}`}
            />
          )}
          {user && (
            <CardSection
              title="Users like you also liked"
              apiUrl={`${apiUrl}/recommendations/recommend_dive_spots/${user.id}`}
            />
          )}
          {user && (
            <AnimalCardSection
              title="Users like you also liked"
              apiUrl={`${apiUrl}/recommendations/recommend_animals/${user.id}`}
            />
          )}
          {user && (
            <CardSection
              title="Close to your Location"
              apiUrl={`${apiUrl}/dive-sites/recommendations/users/${user.id}?w_cat=0.0&w_geo=1.0&w_animal=0.0`}
            />
          )}
          <TopTenSection
            title="Popular Dive Spots"
            apiUrl={`${apiUrl}/recommendations/recommend_top10`}
          />
          <CategoryCardSection
            title="Categories"
            apiUrl={`${apiUrl}/dive-site-categories/`}
          />
        </div>
      </div>
    </>
  );
};

export default Home;
