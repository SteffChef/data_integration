import { DiveSite } from "@/types";
import DiveSpotCard from "./DiveSpotCard";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "./ui/carousel";

interface CardSectionProps {
  title: string;
  apiUrl: string;
}

const CardSection: React.FC<CardSectionProps> = async ({ title, apiUrl }) => {
  const data: DiveSite[] = await fetch(apiUrl).then((res) => res.json());

  return (
    <div className="flex flex-col gap-2">
      <h2 className="font-bold text-2xl">{title}</h2>
      <Carousel className="w-full">
        <CarouselContent className="-ml-1 py-2 pr-4">
          {data.map((item, index) => (
            <CarouselItem
              key={index}
              className="pl-4 sm:basis-1/2 lg:basis-1/3 xl:basis-1/4 2xl:basis-1/5"
            >
              <div className="p-1">
                <DiveSpotCard data={item} />
              </div>
            </CarouselItem>
          ))}
        </CarouselContent>
        <CarouselNext />
        <CarouselPrevious />
      </Carousel>
    </div>
  );
};

export default CardSection;
