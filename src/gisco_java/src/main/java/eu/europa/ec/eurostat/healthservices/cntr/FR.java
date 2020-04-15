package eu.europa.ec.eurostat.healthservices.cntr;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.geotools.referencing.CRS;
import org.locationtech.jts.geom.Coordinate;
import org.locationtech.jts.geom.GeometryFactory;
import org.locationtech.jts.geom.Point;
import org.opengis.referencing.crs.CoordinateReferenceSystem;

import eu.europa.ec.eurostat.healthservices.HCUtil;
import eu.europa.ec.eurostat.healthservices.Validation;
import eu.europa.ec.eurostat.jgiscotools.io.CSVUtil;
import eu.europa.ec.eurostat.jgiscotools.io.GeoData;
import eu.europa.ec.eurostat.jgiscotools.util.ProjectionUtil;

public class FR {

	static String cc = "FR";

	public static void main(String[] args) throws Exception {
		System.out.println("Start");

		List<Map<String,String>> data = CSVUtil.load(HCUtil.path+cc + "/finess_atlasante_18_03_2020/t-finess.csv");
		System.out.println(data.size());

		//filter
		data = data.stream().filter(
				d ->
				!d.get("categ_niv3_code").isBlank()
				//keep only hospitals
				&& "11".equals(d.get("categ_niv3_code").substring(0,2))
				//keep exclude some of them...
				&& !"1111".equals(d.get("categ_niv3_code"))
				&& "ACTUEL".equals(d.get("etat"))
				&& "ET".equals(d.get("type"))
				).collect(Collectors.toList());
		System.out.println(data.size());

		//remove unused columns
		for(String col : new String[]{ "source", "date_maj", "finess8", "etat", "type", "et_finess",
				"ej_finess", "ej_rs", "siren", "siret", "date_autorisation", "date_ouverture",
				"date_maj_finess", "telecopie", "com_code", "gestion_ars",
				"gestion_drjcs", "gestion_drihl", "antenne_possible", "ditep", "dateconv",
				"statut_jur_code","statut_jur_lib", "statut_jur_etat","statut_jur_niv3_code","statut_jur_niv3_lib",
				"statut_jur_niv2_code", "statut_jur_niv2_lib", "statut_jur_niv1_code", "statut_jur_niv1_lib",
				"categ_code","categ_lib","categ_lib_court", "categ_etat","categ_niv3_code","categ_niv2_code",
				"categ_niv2_lib","categ_niv1_code","categ_niv1_lib",
				"mft_code", "mft_lib",
				"geoloc_datemaj"
		})
			CSVUtil.removeColumn(data, col);

		//rename columns
		CSVUtil.renameColumn(data, "finess", "id");

		//names
		data.stream().forEach(d -> {
			String hname = d.get("rs"), etrs = d.get("et_rs");
			if(hname.isBlank() || etrs.length()>hname.length()) hname = etrs;
			d.put("hospital_name", hname);
		} );
		CSVUtil.removeColumn(data, "rs");
		CSVUtil.removeColumn(data, "et_rs");

		//house number
		data.stream().forEach(d -> d.put("house_number", d.get("adresse_num_voie") + d.get("adresse_comp_voie")) );
		CSVUtil.removeColumn(data, "adresse_num_voie");
		CSVUtil.removeColumn(data, "adresse_comp_voie");

		//street
		data.stream().forEach(d -> {
			var tv = d.get("adresse_type_voie");
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
			street += d.get("adresse_nom_voie") + " ";
			street += (d.get("adresse_lieuditbp").contains("BP")? "" : d.get("adresse_lieuditbp"));
			street = street.trim();
			d.put("street", street);
		});
		CSVUtil.removeColumn(data, "adresse_type_voie");
		CSVUtil.removeColumn(data, "adresse_nom_voie");
		CSVUtil.removeColumn(data, "adresse_lieuditbp");


		CSVUtil.renameColumn(data, "adresse_code_postal", "postcode");
		CSVUtil.renameColumn(data, "adresse_lib_routage", "city");
		CSVUtil.renameColumn(data, "telephone", "tel");


		//public_private
		data.stream().forEach(d -> {
			String pp = "";
			switch (d.get("sph_code")) {
			case "": pp = ""; break;
			case "0": pp = ""; break;
			case "1": pp = "public"; break;
			case "2": pp = "public"; break; //PSPH
			case "3": pp = "public"; break; //PSPH
			case "4": pp = "public"; break; //PSPH
			case "5": pp = "private"; break;
			case "6": pp = "private"; break; //Etablissement de santé privé d'intérêt collectif
			case "7": pp = "private"; break; //Etab de santé privé non lucratif, non déclar intérêt collect
			case "9": pp = ""; break; //indeterminé
			default:
				System.out.println("Unhandled codesph = " + d.get("sph_code") + " --- " + d.get("sph_lib") );
				System.out.println(d.get("hospital_name"));
				break;
			}
			d.put("public_private", pp);
		});
		CSVUtil.removeColumn(data, "sph_code");
		CSVUtil.removeColumn(data, "sph_lib");


		//TODO find info somewhere
		CSVUtil.addColumn(data, "emergency", "");

		//
		CSVUtil.renameColumn(data, "categ_niv3_lib", "facility_type");



		//load geom
		List<Map<String,String>> datag = CSVUtil.load(HCUtil.path+cc + "/finess_atlasante_base/geom.csv");
		//finess,loc_score,x_wgs84,y_wgs84
		join(data, "id", datag, "finess", true);
		datag = null;
		CSVUtil.removeColumn(data, "finess");

		//lat lon
		CoordinateReferenceSystem crs = CRS.decode("EPSG:32738");
		GeometryFactory gf = new GeometryFactory();
		data.stream().forEach(d -> {
			if( d.get("x_wgs84") == null ) {
				d.put("lon", "0");
				d.put("lat", "0");
				return;
			}
			double x = Double.parseDouble( d.get("x_wgs84") );
			double y = Double.parseDouble( d.get("y_wgs84") );
			Point pt = (Point) ProjectionUtil.project(gf.createPoint(new Coordinate(x,y)), crs, ProjectionUtil.getWGS_84_CRS());
			d.put("lon", ""+pt.getY());
			d.put("lat", ""+pt.getX());
		} );
		CSVUtil.removeColumn(data, "x_wgs84");
		CSVUtil.removeColumn(data, "y_wgs84");

		//TODO
		CSVUtil.removeColumn(data, "loc_score");
		CSVUtil.addColumn(data, "geo_qual", "-1");
		//CSVUtil.renameColumn(data, "geoloc_precision", "geo_qual");


		//date_extract_finess 2020-03-04 - ref_date 
		SimpleDateFormat df = new SimpleDateFormat("yyyy-MM-dd");
		data.stream().forEach(d -> {
			try {
				Date date = df.parse(d.get("date_extract_finess"));
				d.put("ref_date", HCUtil.dateFormat.format(date));
			} catch (ParseException e) { e.printStackTrace(); }
		} );
		CSVUtil.removeColumn(data, "date_extract_finess");


		//country code. Take into account oversea territories.
		data.stream().forEach(d -> {
			var cc = "";
			switch (d.get("postcode").substring(0,3)) {
			case "971": cc="GP"; break;
			case "972": cc="MQ"; break;
			case "973": cc="GF"; break;
			case "974": cc="RE"; break;
			case "975": cc="PM"; break;
			case "976": cc="YT"; break;
			default: cc="FR"; break;
			}
			d.put("cc", cc);
		} );

		//CSVUtil.addColumns(data, HCUtil.cols, "");
		Validation.validate(data, cc);
		CSVUtil.save(data, HCUtil.path+cc + "/"+cc+".csv");
		GeoData.save(CSVUtil.CSVToFeatures(data, "lon", "lat"), HCUtil.path+cc + "/"+cc+".gpkg", ProjectionUtil.getWGS_84_CRS());

		System.out.println("End");
	}


	public static void join(List<Map<String, String>> data1, String key1, List<Map<String, String>> data2, String key2, boolean printWarnings) {
		//index data2 by key
		var ind2 = new HashMap<String,Map<String,String>>();
		for(Map<String, String> elt : data2) ind2.put(elt.get(key2), elt);

		//join
		for(Map<String, String> elt : data1) {
			String k1 = elt.get(key1);
			Map<String, String> elt2 = ind2.get(k1);
			if(elt2 == null) {System.out.println("No element to join for key: " + k1); continue;}
			elt.putAll(elt2);
		}
	}















	/*
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
	 */



	/*Map<String, CoordinateReferenceSystem> crsDict = Map.of(
	"LAMBERT_93", CRS.decode("EPSG:2154"),
	"UTM_N20", CRS.decode("EPSG:32620"),
	"UTM_N21", CRS.decode("EPSG:32621"),
	"UTM_N22", CRS.decode("EPSG:32622"),
	"UTM_S40", CRS.decode("EPSG:32740"),
	"UTM_S38", CRS.decode("EPSG:32738")
	);*/

}
