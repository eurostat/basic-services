package eu.europa.ec.eurostat.healthservices.cntr;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import eu.europa.ec.eurostat.healthservices.HCUtil;
import eu.europa.ec.eurostat.healthservices.Validation;
import eu.europa.ec.eurostat.jgiscotools.geocoding.BingGeocoder;
import eu.europa.ec.eurostat.jgiscotools.gisco_processes.LocalParameters;
import eu.europa.ec.eurostat.jgiscotools.gisco_processes.services.ServicesGeocoding;
import eu.europa.ec.eurostat.jgiscotools.io.CSVUtil;
import eu.europa.ec.eurostat.jgiscotools.io.GeoData;
import eu.europa.ec.eurostat.jgiscotools.util.ProjectionUtil;

public class FR {

	static String cc = "FR";

	public static void main(String[] args) {
		System.out.println("Start");

		List<Map<String,String>> data = CSVUtil.load(HCUtil.path+cc + "/finess_atlasante_18_03_2020/t-finess.csv");
		System.out.println(data.size());

		//filter
		data = data.stream().filter(
				d ->
				!d.get("categ_niv3_code").isBlank()
				&& "11".equals(d.get("categ_niv3_code").substring(0,2))
				&& "1111".equals(d.get("categ_niv3_code"))
				).collect(Collectors.toList());
		System.out.println(data.size());

		data.stream().forEach(d -> System.out.println(d.get("categ_niv3_code")) );

		/*"source","date_maj","finess","finess8","etat","date_extract_finess",
		"rs","type","ej_finess","ej_rs","et_finess","et_rs","siren","siret",
		"date_autorisation","date_ouverture","date_maj_finess","adresse_num_voie",
		"adresse_comp_voie","adresse_type_voie","adresse_nom_voie",
		"adresse_lieuditbp","adresse_code_postal","adresse_lib_routage",
		"telephone","telecopie","com_code","statut_jur_code","statut_jur_lib",
		"statut_jur_etat","statut_jur_niv3_code","statut_jur_niv3_lib",
		"statut_jur_niv2_code","statut_jur_niv2_lib","statut_jur_niv1_code",
		"statut_jur_niv1_lib","categ_code","categ_lib","categ_lib_court",
		"categ_etat","categ_niv3_code","categ_niv3_lib","categ_niv2_code",
		"categ_niv2_lib","categ_niv1_code","categ_niv1_lib","gestion_ars",
		"gestion_drjcs","gestion_drihl","antenne_possible","ditep","dateconv",
		"mft_code","mft_lib","sph_code","sph_lib",
		"geoloc_x","geoloc_y","geoloc_precision","geoloc_projection","geoloc_datemaj"*/


		System.out.println("End");
	}

	private static void format() {

		//load input data
		var data = CSVUtil.load(HCUtil.path+cc + "/finess_clean.csv");
		System.out.println(data.size());

		var out = new ArrayList<Map<String, String>>();
		for(var r : data) {
			var hf = new HashMap<String, String>();

			//Keep only "Etablissements Hospitaliers", that is: "categagretab = 11**"
			var cat = r.get("categagretab").substring(0,2);
			if(!"11".equals(cat)) continue;


			var id = r.get("nofinesset");
			hf.put("id", id);
			var hname = !r.get("rslongue").equals("")? r.get("rslongue") : r.get("rs");
			hf.put("hospital_name", hname);
			hf.put("site_name", r.get("complrs"));


			hf.put("facility_type", r.get("libcategetab"));

			//public_private
			switch (r.get("codesph")) {
			case "": hf.put("public_private", ""); break;
			case "0": hf.put("public_private", ""); break;
			case "1": hf.put("public_private", "public"); break;
			case "2": hf.put("public_private", "public"); break; //PSPH
			case "3": hf.put("public_private", "public"); break; //PSPH
			case "4": hf.put("public_private", "public"); break; //PSPH
			case "5": hf.put("public_private", "private"); break;
			case "6": hf.put("public_private", "private"); break;
			case "7": hf.put("public_private", "private"); break;
			case "9": hf.put("public_private", ""); break;
			default:
				System.out.println("Unhandled codesph = " + r.get("codesph") + " --- " + r.get("libsph") );
				System.out.println(hname);
				break;
			}

			//TODO find info somewhere
			hf.put("emergency", "");


			//house number
			hf.put("house_number", r.get("numvoie") + r.get("compvoie"));

			//street
			var tv = r.get("typvoie");
			switch (tv) {
			case "": break;
			case "R": tv="RUE"; break;
			case "AV": tv="AVENUE"; break;
			case "BD": tv="BOULEVARD"; break;
			case "PL": tv="PLACE"; break;
			case "RTE": tv="ROUTE"; break;
			case "IMP": tv="IMPASSE"; break;
			case "CHE": tv="CHEMIN"; break;
			case "QUA": tv="QUAI"; break;
			case "PROM": tv="PROMENADE"; break;
			case "PASS": tv="PASSAGE"; break;
			case "ALL": tv="ALLEE"; break;
			//default: System.out.println(tv);
			}
			String street = "";
			street += ("".equals(tv) || tv==null)? "" : tv + " ";
			street += r.get("voie") + " ";
			street += (r.get("lieuditbp").contains("BP")? "" : r.get("lieuditbp"));
			street = street.trim();
			hf.put("street", street);

			//postcode - TODO convert cedex to noncedex?
			var lia = r.get("ligneacheminement");
			hf.put("postcode", lia.substring(0, 5));

			//city
			var city = lia.substring(6, lia.length());
			for(int cedex = 30; cedex>0; cedex--) city = city.replace("CEDEX " + cedex, "");
			city = city.replace("CEDEX", "");
			city = city.trim();
			hf.put("city", city);
			if(city==null || city.equals("")) System.err.println("No city for " + id);

			//country code. Take into account oversea territories.
			var cc = "";
			switch (hf.get("postcode").substring(0,3)) {
			case "971": cc="GP"; break;
			case "972": cc="MQ"; break;
			case "973": cc="GF"; break;
			case "974": cc="RE"; break;
			case "975": cc="PM"; break;
			case "976": cc="YT"; break;
			default: cc="FR"; break;
			}
			hf.put("cc", cc);

			hf.put("tel", r.get("telephone"));

			//if("".equals(hf.get("street"))) System.out.println(hf.get("city") + "  ---  " + hf.get("hospital_name"));
			out.add(hf);
		}

		CSVUtil.addColumn(out, "ref_date", "06/03/2020");
		CSVUtil.addColumn(out, "pub_date", "");
		CSVUtil.addColumn(out, "geo_qual", "-1");
		CSVUtil.addColumn(out, "lon", "0");
		CSVUtil.addColumn(out, "lat", "0");
		CSVUtil.addColumns(out, HCUtil.cols, "");
		Validation.validate(out, cc);

		System.out.println("Save " + out.size());
		CSVUtil.save(out, HCUtil.path+cc + "/"+cc+"_formated.csv");
	}


	public static void geocode() {

		//load input data
		var data = CSVUtil.load(HCUtil.path+cc + "/"+cc+"_formated.csv");
		System.out.println(data.size());

		LocalParameters.loadProxySettings();
		ServicesGeocoding.set(BingGeocoder.get(), data, "lon", "lat", true, true);

		CSVUtil.addColumns(data, HCUtil.cols, "");
		Validation.validate(data, cc);
		CSVUtil.save(data, HCUtil.path+cc + "/"+cc+".csv");
		GeoData.save(CSVUtil.CSVToFeatures(data, "lon", "lat"), HCUtil.path+cc + "/"+cc+".gpkg", ProjectionUtil.getWGS_84_CRS());

	}





	/*/
			GeometryFactory gf = new GeometryFactory();
			CoordinateReferenceSystem LAMBERT_93 = CRS.decode("EPSG:2154");
			CoordinateReferenceSystem UTM_N20 = CRS.decode("EPSG:32620");
			CoordinateReferenceSystem UTM_N21 = CRS.decode("EPSG:32621");
			CoordinateReferenceSystem UTM_N22 = CRS.decode("EPSG:32622");
			CoordinateReferenceSystem UTM_S40 = CRS.decode("EPSG:32740");
			CoordinateReferenceSystem UTM_S38 = CRS.decode("EPSG:32738");*/


	/*/get CRS
				CoordinateReferenceSystem crs = null;
				switch (r.get("crs")) {
				case "LAMBERT_93": crs = LAMBERT_93; break;
				case "UTM_N20": crs = UTM_N20; break;
				case "UTM_N21": crs = UTM_N21; break;
				case "UTM_N22": crs = UTM_N22; break;
				case "UTM_S40": crs = UTM_S40; break;
				case "UTM_S38": crs = UTM_S38; break;
				default: System.out.println(r.get("crs")); break;
				}*/

	/*/change crs to lon/lat
				double x = Double.parseDouble( r.get("coordxet") );
				double y = Double.parseDouble( r.get("coordyet") );
				Point pt = (Point) ProjectionUtil.project(gf.createPoint(new Coordinate(x,y)), crs, ProjectionUtil.getWGS_84_CRS());
				hf.put("lon", ""+pt.getY());
				hf.put("lat", ""+pt.getX());*/

}
