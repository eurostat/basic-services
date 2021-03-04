/**
 * 
 */
package eu.europa.ec.eurostat.basicservices;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.attribute.FileTime;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Collection;
import java.util.List;
import java.util.Map;

import org.locationtech.jts.geom.Coordinate;

import eu.europa.ec.eurostat.jgiscotools.deprecated.NUTSUtils;
import eu.europa.ec.eurostat.jgiscotools.feature.Feature;
import eu.europa.ec.eurostat.jgiscotools.io.CSVUtil;
import eu.europa.ec.eurostat.jgiscotools.io.geo.CRSUtil;
import eu.europa.ec.eurostat.jgiscotools.io.geo.GeoData;

/**
 * Generic publication script for basic services.
 * 
 * - Copy country CSV files to github repository.
 * - Set the publication date and country name.
 * - Combine them in the all.csv file.
 * - Convert as GeoJSON and GPKG format.
 * 
 * @author julien Gaffuri
 *
 */
public class BasicServicePublication {


	/**
	 * @param serviceType 
	 * @param inDataPath 
	 * @param destinationBasePath 
	 * @param ccs 
	 * @param cols_ 
	 * @param ats 
	 * @param args
	 */
	public static void publish(String serviceType, String inDataPath, String destinationBasePath, String[] ccs, List<String> cols_, AttributeTypeSetter ats) {
		System.out.println("Start");

		//Service - Education/EUR/
		//Service - Service - Health/EUR/
		String folder = "education".equals(serviceType)? "Service - Education" : "Service - Health";
		String destinationDataPath = destinationBasePath + folder + "/EUR/";

		//get publication date
		String timeStamp = BasicServicesUtil.dateFormat.format(Calendar.getInstance().getTime());
		System.out.println("Publication date: " + timeStamp);

		//make outpur folders
		new File(destinationDataPath + "csv/").mkdirs();
		new File(destinationDataPath + "geojson/").mkdirs();
		new File(destinationDataPath + "gpkg/").mkdirs();

		var changed = false;
		for(String cc : ccs) {

			var inCsvFile = inDataPath + cc+"/"+cc+".csv";
			var outCsvFile = destinationDataPath+"csv/"+cc+".csv";

			//compare file dates, skip the ones that have not been updated
			if(new File(outCsvFile).exists())
				try {
					FileTime tIn = Files.getLastModifiedTime(new File(inCsvFile).toPath());
					FileTime tOut = Files.getLastModifiedTime(new File(outCsvFile).toPath());
					if(tOut.compareTo(tIn) >= 0) {
						System.out.println("No change found for: " + cc);
						//if(tOut.compareTo(tIn) > 0)
						//	Files.copy(new File(outCsvFile).toPath(), new File(inCsvFile).toPath(), StandardCopyOption.REPLACE_EXISTING);
						continue;
					}
				} catch (IOException e) { e.printStackTrace(); }

			changed = true;

			System.out.println("*** " + cc);
			System.out.println("Update");

			//load data
			ArrayList<Map<String, String>> data = CSVUtil.load(inCsvFile);
			System.out.println(data.size());

			//cc, country
			String cntr = NUTSUtils.getName(cc);
			if(cntr == null) System.err.println("cc: " + cc);
			if("DE".equals(cc)) cntr = "Germany";
			//CSVUtil.setValue(data, "cc", cc); //do not apply that - overseas territories
			CSVUtil.setValue(data, "country", cntr);

			//apply publication date
			CSVUtil.setValue(data, "pub_date", timeStamp);

			//apply geo_qual
			//replace(data, "geo_qual", null, "-1");
			//replace(data, "geo_qual", "", "-1");
			//CSVUtil.removeColumn(data, "geo_matching");
			//CSVUtil.removeColumn(data, "geo_confidence");

			//export as geojson and GPKG
			CSVUtil.save(data, outCsvFile, cols_);
			Collection<Feature> fs = CSVUtil.CSVToFeatures(data, "lon", "lat");
			ats.setAttributeTypes(fs);
			GeoData.save(fs, destinationDataPath+"geojson/"+cc+".geojson", CRSUtil.getWGS_84_CRS());
			GeoData.save(fs, destinationDataPath+"gpkg/"+cc+".gpkg", CRSUtil.getWGS_84_CRS());
		}

		//handle "all" files
		if(changed) {

			var all = new ArrayList<Map<String, String>>();
			for(String cc : ccs)
				all.addAll( CSVUtil.load(destinationDataPath+"csv/"+cc+".csv") );

			//append cc to id
			for(Map<String, String> h : all) {
				String cc = h.get("cc");
				String id = h.get("id");
				if(id == null || "".equals(id)) {
					System.err.println("No identifier for items in " + cc);
					break;
				}
				String cc_ = id.length()>=2? id.substring(0, 2) : "";
				if(cc_.equals(cc)) continue;
				h.put("id", cc + "_" + id);
			}

			//export all
			System.out.println("*** All");
			System.out.println(all.size());
			CSVUtil.save(all, destinationDataPath+"csv/all.csv", cols_);
			Collection<Feature> fs = CSVUtil.CSVToFeatures(all, "lon", "lat");
			ats.setAttributeTypes(fs);
			GeoData.save(fs, destinationDataPath + "geojson/all.geojson", CRSUtil.getWGS_84_CRS());
			GeoData.save(fs, destinationDataPath + "gpkg/all.gpkg", CRSUtil.getWGS_84_CRS());
			

			{
				//export for web
				ArrayList<Map<String, String>> data = CSVUtil.load(destinationDataPath+"csv/all.csv");
				for(Map<String, String> d : data) {
					//load lat/lon
					double lon = Double.parseDouble(d.get("lon"));
					d.remove("lon");
					double lat = Double.parseDouble(d.get("lat"));
					d.remove("lat");

					//project to LAEA
					Coordinate c = CRSUtil.project(new Coordinate(lat,lon), CRSUtil.getWGS_84_CRS(), CRSUtil.getETRS89_LAEA_CRS());
					d.put("x", ""+(int)c.y);
					d.put("y", ""+(int)c.x);

					d.remove("id");
					d.remove("cc");
					d.remove("geo_qual");
				}

				//save
				new File(destinationBasePath + "map/"+serviceType+"/").mkdirs();
				CSVUtil.save(data, destinationBasePath + "map/"+serviceType+"/hcs.csv");
			}
		}

		System.out.println("End");
	}


	/**
	 * A function specifying how to set the type of some attributes.
	 * 
	 * @author julien Gaffuri
	 *
	 */
	public interface AttributeTypeSetter {
		/**
		 * @param fs The list of features to set the attributes of.
		 */
		void setAttributeTypes(Collection<Feature> fs);
	}

}
