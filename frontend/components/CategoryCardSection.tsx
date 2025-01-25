import { DiveSiteCategory } from "@/types";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "./ui/carousel";
import CategoryDiveSiteCard from "./CategoryDiveSiteCard";

interface CategoryCardSectionProps {
  title: string;
  apiUrl: string;
}

const CategoryCardSection: React.FC<CategoryCardSectionProps> = async ({
  title,
  apiUrl,
}) => {
  const data: DiveSiteCategory[] = await fetch(apiUrl).then((res) =>
    res.json()
  );

  return (
    <div className="flex flex-col gap-2">
      <h2 className="font-bold text-2xl">{title}</h2>
      <Carousel className="w-full">
        <CarouselContent className="-ml-1 py-2 pr-4">
          {data.map((item, index) => (
            <CarouselItem
              key={index}
              className=" basis-1/2 sm:basis-1/3 lg:basis-1/4 xl:basis-1/5 2xl:basis-1/6"
            >
              <div className="p-1">
                <CategoryDiveSiteCard data={item} />
              </div>
            </CarouselItem>
          ))}
        </CarouselContent>
        <CarouselPrevious />
        <CarouselNext />
      </Carousel>
    </div>
  );
};

export default CategoryCardSection;
