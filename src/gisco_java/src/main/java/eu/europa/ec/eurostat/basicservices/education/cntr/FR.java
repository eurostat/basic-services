package eu.europa.ec.eurostat.basicservices.education.cntr;

import java.io.File;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.apache.commons.csv.CSVFormat;

import eu.europa.ec.eurostat.basicservices.education.EducationUtil;
import eu.europa.ec.eurostat.jgiscotools.gisco_processes.LocalParameters;
import eu.europa.ec.eurostat.jgiscotools.io.CSVUtil;
import eu.europa.ec.eurostat.jgiscotools.io.web.HTTPUtil;

public class FR {

	public static void main(String[] args) {
		System.out.println("Start");
		/*
		#https://www.education.gouv.fr/
			#https://data.education.gouv.fr/
			#https://data.education.gouv.fr/map/

			# Annuaire de l'éducation
			# Annuaire de l'éducation : données sur les établissements publics et privés ouverts situés en France. Le jeu de données couvre le premier degré, le second degré, les Centre d'Information et d'Orientation ainsi que les établissements administratifs.
			# fr-en-annuaire-education
			# 66460

			#https://data.education.gouv.fr/explore/dataset/fr-en-annuaire-education/table/?disjunctive.nom_etablissement&disjunctive.type_etablissement&disjunctive.appartenance_education_prioritaire&disjunctive.type_contrat_prive&disjunctive.code_type_contrat_prive&disjunctive.pial
			#https://data.education.gouv.fr/explore/dataset/fr-en-annuaire-education/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B
		 */

		//download data when FR_raw.csv file is not present
		String url = "https://data.education.gouv.fr/explore/dataset/fr-en-annuaire-education/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B";
		String inFilePath = EducationUtil.path + "FR/FR_raw.csv";
		if(!new File(inFilePath).exists()) {
			System.out.println("Download...");
			LocalParameters.loadProxySettings();
			HTTPUtil.downloadFromURL(url, inFilePath);
		}

		// load data
		CSVFormat csvF = CSVFormat.DEFAULT.withFirstRecordAsHeader().withDelimiter(';');
		List<Map<String, String>> data = CSVUtil.load(inFilePath, csvF);
		System.out.println(data.size());

		//Identifiant_de_l_etablissement
		//
		//Adresse_1;Adresse_2;Adresse_3;Code postal;Code_commune;Nom_commune
		//Code_departement;Code_academie;Code_region
		//;Ecole_maternelle;Ecole_elementaire
		//Voie_generale;Voie_technologique;Voie_professionnelle;
		//Telephone;Fax;Web;Mail;
		//Restauration;Hebergement;ULIS;Apprentissage;Segpa;
		//Section_arts;Section_cinema;Section_theatre;Section_sport;Section_internationale;Section_europeenne;
		//Lycee_Agricole;Lycee_militaire;Lycee_des_metiers;
		//Post_BAC;Appartenance_Education_Prioritaire;GRETA;SIREN_SIRET
		//;Nombre_d_eleves;
		//Fiche_onisep;position
		//;Type_contrat_prive;Libelle_departement;Libelle_academie;Libelle_region;
		//coordonnee_X;coordonnee_Y;epsg;nom_circonscription;
		//latitude;longitude;precision_localisation;
		//date_ouverture;
		//date_maj_ligne
		//;etat;ministere_tutelle;etablissement_multi_lignes;
		//"rpi_concentre";"rpi_disperse"
		//;"code_nature";"libelle_nature;
		


		//remove useless columns
		CSVUtil.removeColumn(data, "Code_type_contrat_prive", "PIAL", "etablissement_mere", "type_rattachement_etablissement_mere", "code_bassin_formation", "libelle_bassin_formation");
	
		//filter Type_etablissement
		//[Service Administratif, Ecole, Lycée, EREA, Collège, Information et orientation]
		data = data.stream().filter(
				d -> { return true; }
				).collect(Collectors.toList());
		System.out.println(data.size());

		//rename columns
		CSVUtil.renameColumn(data, "Nom_etablissement", "name");

		//CSVUtil.getUniqueValues(data, "Statut_public_prive", true);
		//[, Privé, Public, -]


		
		//Collection<Map<String, String>> out = new ArrayList<Map<String, String>>();

		//for (Map<String, String> s : data) {
		//}

		//Validation.validate(true, out, "FR");

		//save
		//System.out.println(out.size());
		//CSVUtil.save(out, EducationUtil.path + "FR/FR.csv");
		//GeoData.save(CSVUtil.CSVToFeatures(out, "lon", "lat"), EducationUtil.path + "FR/FR.gpkg", CRSUtil.getWGS_84_CRS());



		System.out.println("End");
	}

}
